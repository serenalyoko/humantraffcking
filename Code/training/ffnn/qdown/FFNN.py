import argparse, random, json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    classification_report,
)

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_labels(labels_path: str) -> np.ndarray:
    ext = Path(labels_path).suffix.lower()
    if ext == ".parquet":
        df = pd.read_parquet(labels_path)
    elif ext == ".csv":
        df = pd.read_csv(labels_path)
    elif ext == ".pkl":
        df = pd.read_pickle(labels_path)
    else:
        raise ValueError(f"Unsupported label file type: {ext}")

    if "label" not in df.columns:
        raise ValueError("Missing 'label' column in labels file.")

    mapping = {"safe": 0, "risk": 1}
    y = df["label"].map(mapping)
    if y.isna().any():
        y = df["label"].astype(int)

    return y.values


def choose_threshold_by_f1(y_true, p):
    ts = np.linspace(0, 1, 500)
    best_t, best_f1 = 0.5, -1.0
    for t in ts:
        f1 = f1_score(y_true, (p >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_t, best_f1 = t, f1
    return best_t


def compute_metrics(y_true, prob, thr):
    y_pred = (prob >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fnr = fn / (fn + tp + 1e-9)
    return dict(
        ROC_AUC=roc_auc_score(y_true, prob),
        PR_AUC=average_precision_score(y_true, prob),
        FNR=fnr,
        precision=precision_score(y_true, y_pred, zero_division=0),
        recall=recall_score(y_true, y_pred, zero_division=0),
        accuracy=accuracy_score(y_true, y_pred),
        f1=f1_score(y_true, y_pred, zero_division=0),
        threshold=float(thr),
    )


class FFNN(nn.Module):
    def __init__(self, in_dim, hidden=256, dropout=0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


class EmbDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.from_numpy(X).float()
        self.y = torch.from_numpy(y).float()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        return self.X[i], self.y[i]


def train_one_fold(X, y, train_idx, test_idx, device, args, fold):
    tr_idx, val_idx = train_test_split(
        train_idx,
        test_size=args.val_ratio,
        random_state=args.seed,
        stratify=y[train_idx] if len(np.unique(y[train_idx])) > 1 else None,
    )
    X_tr, y_tr = X[tr_idx], y[tr_idx]
    X_val, y_val = X[val_idx], y[val_idx]
    X_te, y_te = X[test_idx], y[test_idx]

    model = FFNN(in_dim=X.shape[1], hidden=args.hidden, dropout=args.dropout).to(device)

    pos_ratio = (y_tr == 1).mean()
    neg_ratio = 1 - pos_ratio
    pos_weight_value = (neg_ratio / pos_ratio) if pos_ratio > 0 else 1.0
    pos_weight = torch.tensor([pos_weight_value], device=device, dtype=torch.float32)

    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    tr_loader = DataLoader(EmbDataset(X_tr, y_tr), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(EmbDataset(X_val, y_val), batch_size=1024, shuffle=False)
    test_loader = DataLoader(EmbDataset(X_te, y_te), batch_size=1024, shuffle=False)

    best_state, best_ap, patience = None, -1.0, args.patience

    for ep in range(1, args.epochs + 1):
        model.train()
        run_loss = 0.0
        for xb, yb in tr_loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()
            run_loss += loss.item() * xb.size(0)

        model.eval()
        with torch.no_grad():
            val_probs = np.concatenate(
                [
                    torch.sigmoid(model(xb.to(device))).detach().cpu().numpy()
                    for xb, _ in val_loader
                ]
            )
        ap = average_precision_score(y_val, val_probs)

        if ap > best_ap + 1e-5:
            best_ap = ap
            best_state = {k: v.cpu() for k, v in model.state_dict().items()}
            torch.save(best_state, f"ffnn_{str(args.labels).split('/')[-1].split('.')[0]}_best_model_fold_{fold}.pt")
            patience = args.patience
        else:
            patience -= 1

        if args.verbose:
            print(f"Epoch {ep:02d} | val_PR_AUC={ap:.4f} | best={best_ap:.4f}")

        if patience <= 0:
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        val_probs = np.concatenate(
            [
                torch.sigmoid(model(xb.to(device))).detach().cpu().numpy()
                for xb, _ in val_loader
            ]
        )
    thr = choose_threshold_by_f1(y_val, val_probs)

    with torch.no_grad():
        test_probs = np.concatenate(
            [
                torch.sigmoid(model(xb.to(device))).detach().cpu().numpy()
                for xb, _ in test_loader
            ]
        )
    y_pred_te = (test_probs >= thr).astype(int)

    m = compute_metrics(y_te, test_probs, thr)

    return m, y_te, y_pred_te, test_probs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--embeddings", type=str, default="labeled_jd_downsampled_qwen3_8b.npy")
    p.add_argument("--labels", type=str, default="labeled_jd_downsampled_with_Qwen_embeddings.parquet")
    p.add_argument("--kfold", type=int, default=5)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch_size", type=int, default=256)
    p.add_argument("--hidden", type=int, default=256)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight_decay", type=float, default=1e-4)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument("--val_ratio", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--out_dir", type=str, default="ffnn_downsample_results")
    args = p.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    X = np.load(args.embeddings).astype(np.float32)
    y = load_labels(args.labels)
    print(f"[Info] Loaded embeddings {X.shape}, labels {y.shape}")

    n_samples = len(y)

    ext = Path(args.labels).suffix.lower()
    if ext == ".parquet":
        df_labels = pd.read_parquet(args.labels)
    elif ext == ".csv":
        df_labels = pd.read_csv(args.labels)
    elif ext == ".pkl":
        df_labels = pd.read_pickle(args.labels)
    else:
        raise ValueError(f"Unsupported label file type: {ext}")

    skf = StratifiedKFold(n_splits=args.kfold, shuffle=True, random_state=args.seed)

    all_m = []

    oof_true = np.zeros(n_samples, dtype=int)
    oof_pred = np.zeros(n_samples, dtype=int)
    oof_prob = np.zeros(n_samples, dtype=float)

    for i, (tr, te) in enumerate(skf.split(X, y), 1):
        print(f"\n==== Fold {i}/{args.kfold} ====")
        m, y_te, y_pred_te, prob_te = train_one_fold(X, y, tr, te, device, args, i)
        all_m.append(m)

        oof_true[te] = y_te
        oof_pred[te] = y_pred_te
        oof_prob[te] = prob_te

    y_true_all = oof_true
    y_pred_all = oof_pred
    prob_all = oof_prob

    print("\n====== Overall Classification Report (all folds, OOF) ======")
    print(
        classification_report(
            y_true_all,
            y_pred_all,
            target_names=["safe", "risk"],
            digits=2,
        )
    )
    overall_roc = roc_auc_score(y_true_all, prob_all)
    overall_pr = average_precision_score(y_true_all, prob_all)
    print(f"ROC-AUC: {overall_roc}")
    print(f"PR-AUC:  {overall_pr}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df_metrics = pd.DataFrame(all_m)
    csv_path = out_dir / f"{str(args.labels).split('/')[-1].split('.')[0]}.per_fold_metrics.csv"
    df_metrics.to_csv(csv_path, index=False)
    print(f"\nSaved metrics to: {csv_path}")

    summary = {
        f"{k}_mean": float(df_metrics[k].mean())
        for k in df_metrics.columns
        if df_metrics[k].dtype != "O"
    }
    summary.update(
        {
            f"{k}_std": float(df_metrics[k].std())
            for k in df_metrics.columns
            if df_metrics[k].dtype != "O"
        }
    )

    result = {
        "fold_metrics": all_m,
        "summary": summary,
        "overall": {
            "ROC_AUC": float(overall_roc),
            "PR_AUC": float(overall_pr),
        },
    }

    json_path = out_dir / f"{str(args.labels).split('/')[-1].split('.')[0]}.ffnn_results.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved JSON results to: {json_path}")

    idx = np.arange(n_samples)
    inv_map = {0: "safe", 1: "risk"}
    true_label_str = [inv_map.get(int(v), "") for v in y_true_all]
    pred_label_str = [inv_map.get(int(v), "") for v in y_pred_all]

    if "description" in df_labels.columns:
        desc_col = df_labels["description"]
    else:
        desc_col = pd.Series([None] * n_samples)

    oof_df = pd.DataFrame(
        {
            "idx": idx,
            "description": desc_col,
            "true_label": y_true_all,
            "true_label_str": true_label_str,
            "pred_prob": prob_all,
            "pred_label": y_pred_all,
            "pred_label_str": pred_label_str,
        }
    )

    oof_csv_path = out_dir / f"{str(args.labels).split('/')[-1].split('.')[0]}.oof_predictions.csv"
    oof_df.to_csv(oof_csv_path, index=False)
    print(f"Saved OOF predictions to: {oof_csv_path}")


if __name__ == "__main__":
    main()