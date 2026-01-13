import argparse, json, os, random
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    confusion_matrix, precision_score, recall_score, roc_curve, auc,
    accuracy_score, classification_report
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_labels(labels_path: str) -> pd.Series:
    ext = Path(labels_path).suffix.lower()
    usecols = ["label"]
    if ext == ".parquet":
        df = pd.read_parquet(labels_path, columns=usecols)
    elif ext == ".csv":
        df = pd.read_csv(labels_path, usecols=usecols)
    else:
        raise ValueError(f"labels must be .csv or .parquet, got {ext}")
    mapping = {"safe": 0, "risk": 1}
    y = df["label"].map(mapping).astype(np.int64)
    return y


def choose_threshold_by_f1(y_true: np.ndarray, p: np.ndarray):
    ts = np.linspace(0.0, 1.0, 500)
    best_t, best_f1 = 0.5, -1.0
    for t in ts:
        pred = (p >= t).astype(np.int64)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return best_t


def choose_threshold_for_recall(y_true: np.ndarray, p: np.ndarray, recall_target=0.9):
    ts = np.linspace(0.0, 1.0, 2000)
    chosen = ts[0]
    for t in ts:
        pred = (p >= t).astype(np.int64)
        rec = recall_score(y_true, pred, zero_division=0)
        if rec >= recall_target:
            chosen = t
            break
    return chosen


def compute_metrics(y_true: np.ndarray, prob: np.ndarray, thr: float):
    y_pred = (prob >= thr).astype(np.int64)
    roc = roc_auc_score(y_true, prob)
    ap = average_precision_score(y_true, prob)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    acc = (tp + tn) / max((tp + tn + fp + fn), 1)
    return {
        "ROC_AUC": float(roc),
        "PR_AUC": float(ap),
        "FNR": float(fnr),
        "precision": float(prec),
        "recall": float(rec),
        "F1": float(f1),
        "accuracy": float(acc),
        "threshold": float(thr),
    }


def plot_confusion_matrix(cm, out_path: Path, title: str):
    fig = plt.figure()
    plt.imshow(cm, interpolation="nearest")
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.xticks([0, 1], ["0", "1"])
    plt.yticks([0, 1], ["0", "1"])
    for i in range(2):
        for j in range(2):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def plot_mean_roc(fprs, tprs, aucs, out_path: Path, title: str):
    mean_fpr = np.linspace(0, 1, 1001)
    interp_tprs = []
    for fpr, tpr in zip(fprs, tprs):
        interp = np.interp(mean_fpr, fpr, tpr)
        interp[0] = 0.0
        interp_tprs.append(interp)
    mean_tpr = np.mean(interp_tprs, axis=0)
    std_tpr = np.std(interp_tprs, axis=0)
    mean_auc = float(np.mean(aucs))
    std_auc = float(np.std(aucs))
    fig = plt.figure()
    plt.plot(mean_fpr, mean_tpr, label=f"Mean ROC (AUC = {mean_auc:.3f} ± {std_auc:.3f})")
    plt.fill_between(mean_fpr, np.maximum(mean_tpr - std_tpr, 0), np.minimum(mean_tpr + std_tpr, 1), alpha=0.2)
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


class EmbDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.from_numpy(X.astype(np.float32, copy=False))
        self.y = torch.from_numpy(y.astype(np.int64, copy=False))

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class FFNN(nn.Module):
    def __init__(self, in_dim=1024, hidden=256, dropout=0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_one_fold(X, y, train_idx, test_idx, device, args):
    tr_idx, val_idx = train_test_split(
        train_idx,
        test_size=args.val_ratio,
        random_state=args.seed,
        stratify=y[train_idx] if len(np.unique(y[train_idx])) > 1 else None,
    )
    X_tr, y_tr = X[tr_idx], y[tr_idx]
    X_val, y_val = X[val_idx], y[val_idx]
    X_te, y_te = X[test_idx], y[test_idx]
    train_loader = DataLoader(EmbDataset(X_tr, y_tr), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(EmbDataset(X_val, y_val), batch_size=1024, shuffle=False)
    test_loader = DataLoader(EmbDataset(X_te, y_te), batch_size=1024, shuffle=False)
    model = FFNN(in_dim=X.shape[1], hidden=args.hidden, dropout=args.dropout).to(device)
    pos_ratio = (y_tr == 1).sum() / max(len(y_tr), 1)
    neg_ratio = 1 - pos_ratio
    base_weight = (neg_ratio / pos_ratio) if pos_ratio > 0 else 1.0
    pos_weight = torch.tensor([base_weight * args.pos_weight_factor], dtype=torch.float32, device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    best_val_ap = -1.0
    best_state = None
    patience_left = args.patience
    for epoch in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.float().to(device)
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            running += loss.item() * xb.size(0)
        train_loss = running / max(len(train_loader.dataset), 1)
        model.eval()
        with torch.no_grad():
            val_probs = np.concatenate(
                [
                    torch.sigmoid(model(xb.to(device))).cpu().numpy()
                    for xb, _ in val_loader
                ]
            ) if len(val_loader) > 0 else np.array([])
        val_ap = average_precision_score(y_val, val_probs) if val_probs.size else 0.0
        if val_ap > best_val_ap + 1e-5:
            best_val_ap = val_ap
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            patience_left = args.patience
            torch.save(best_state, f"bge_unbalanced_best_model_epoch_{epoch}.pt")
        else:
            patience_left -= 1
        if args.verbose:
            print(
                f"Epoch {epoch:02d} | train_loss={train_loss:.4f} | "
                f"val_PR_AUC={val_ap:.4f} | best={best_val_ap:.4f} | "
                f"pos_weight={pos_weight.item():.2f}"
            )
        if patience_left <= 0:
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        val_probs = np.concatenate(
            [
                torch.sigmoid(model(xb.to(device))).cpu().numpy()
                for xb, _ in val_loader
            ]
        ) if len(val_loader) > 0 else np.array([])
    if args.decision == "recall":
        thr = choose_threshold_for_recall(y_val, val_probs, args.recall_target) if val_probs.size else 0.5
    else:
        thr = choose_threshold_by_f1(y_val, val_probs) if val_probs.size else 0.5
    with torch.no_grad():
        test_probs = np.concatenate(
            [
                torch.sigmoid(model(xb.to(device))).cpu().numpy()
                for xb, _ in test_loader
            ]
        ) if len(test_loader) > 0 else np.array([])
    metrics = (
        compute_metrics(y_te, test_probs, thr)
        if test_probs.size
        else {
            "ROC_AUC": 0.0,
            "PR_AUC": 0.0,
            "FNR": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "F1": 0.0,
            "accuracy": 0.0,
            "threshold": float(thr),
        }
    )
    if args.verbose:
        print(
            f"[Fold] threshold={metrics['threshold']:.3f} | "
            f"precision={metrics['precision']:.3f} | "
            f"recall={metrics['recall']:.3f} | FNR={metrics['FNR']:.3f}"
        )
    y_pred = (test_probs >= thr).astype(np.int64) if test_probs.size else np.zeros_like(y_te)
    cm = confusion_matrix(y_te, y_pred, labels=[0, 1])
    fpr, tpr, _ = roc_curve(y_te, test_probs) if test_probs.size else (np.array([0, 1]), np.array([0, 1]), None)
    fold_auc = auc(fpr, tpr) if test_probs.size else 0.5
    return metrics, (y_te, test_probs, y_pred, cm, fpr, tpr, fold_auc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", type=str, required=True)
    parser.add_argument("--labels", type=str, required=True)
    parser.add_argument("--kfold", type=int, default=5)
    parser.add_argument("--val_ratio", type=float, default=0.2)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--hidden", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight_decay", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--pos_weight_factor", type=float, default=5.0)
    parser.add_argument("--decision", choices=["f1", "recall"], default="f1")
    parser.add_argument("--recall_target", type=float, default=0.90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--out_dir", type=str, default="ffnn_cv_plots")
    parser.add_argument("--save_fold_preds", action="store_true")
    args = parser.parse_args()
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if args.verbose:
        print("Device:", device)
    meta = json.load(open(args.meta, "r"))
    emb_path = meta["doc_embeddings_file"]
    meta_dir = str(Path(args.meta).parent)
    emb_path = emb_path if os.path.isabs(emb_path) else os.path.join(meta_dir, emb_path)
    X = np.load(emb_path)
    y = load_labels(args.labels).values
    assert X.shape[0] == y.shape[0], "Rows mismatch between embeddings and labels!"
    n_samples = len(y)
    ext = Path(args.labels).suffix.lower()
    if ext == ".parquet":
        df_labels = pd.read_parquet(args.labels)
    elif ext == ".csv":
        df_labels = pd.read_csv(args.labels)
    else:
        raise ValueError(f"labels must be .csv or .parquet, got {ext}")
    skf = StratifiedKFold(n_splits=args.kfold, shuffle=True, random_state=args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_metrics = []
    fold_details = []
    oof_true = np.zeros(n_samples, dtype=int)
    oof_pred = np.zeros(n_samples, dtype=int)
    oof_prob = np.zeros(n_samples, dtype=float)
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), start=1):
        print(f"\n==== Fold {fold}/{args.kfold} ====")
        m, info = train_one_fold(X, y, train_idx, test_idx, device, args)
        all_metrics.append(m)
        fold_details.append(info)
        y_te, probs, y_pred, cm, fpr, tpr, fold_auc = info
        oof_true[test_idx] = y_te
        oof_pred[test_idx] = y_pred
        oof_prob[test_idx] = probs
        if args.plot:
            plot_confusion_matrix(cm, out_dir / f"cm_fold{fold}.png", title=f"Confusion Matrix - Fold {fold}")
            fig = plt.figure()
            plt.plot(fpr, tpr, label=f"Fold {fold} (AUC={fold_auc:.3f})")
            plt.plot([0, 1], [0, 1], linestyle="--")
            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.title(f"ROC Curve - Fold {fold}")
            plt.legend(loc="lower right")
            plt.tight_layout()
            fig.savefig(out_dir / f"roc_fold{fold}.png", dpi=180)
            plt.close(fig)
            if args.save_fold_preds:
                np.savez_compressed(
                    out_dir / f"fold{fold}_preds.npz",
                    y_true=y_te,
                    y_prob=probs,
                    y_pred=y_pred,
                )
    def agg(key):
        vals = [m[key] for m in all_metrics]
        return float(np.mean(vals)), float(np.std(vals))
    roc_m, roc_s = agg("ROC_AUC")
    pr_m, pr_s = agg("PR_AUC")
    fnr_m, fnr_s = agg("FNR")
    print("\n===== Cross-Validation Summary =====")
    print(f"ROC_AUC: {roc_m:.4f} ± {roc_s:.4f}")
    print(f"PR_AUC : {pr_m:.4f} ± {pr_s:.4f}")
    print(f"FNR    : {fnr_m:.4f} ± {fnr_s:.4f}")
    if args.plot and len(fold_details) > 0:
        fprs = [fd[4] for fd in fold_details]
        tprs = [fd[5] for fd in fold_details]
        aucs = [fd[6] for fd in fold_details]
        plot_mean_roc(fprs, tprs, aucs, out_dir / "roc_mean.png", title="Mean ROC across folds")
    per_fold_rows = []
    for i, m in enumerate(all_metrics, start=1):
        row = {"fold": i}
        row.update(m)
        per_fold_rows.append(row)
    pd.DataFrame(per_fold_rows).to_csv(out_dir / "per_fold_metrics.csv", index=False)
    best_idx = int(np.argmax([m["F1"] for m in all_metrics]))
    best_y_true, best_probs, best_y_pred, best_cm, *_ = fold_details[best_idx]
    best_acc = accuracy_score(best_y_true, best_y_pred)
    best_f1_macro = f1_score(best_y_true, best_y_pred, average="macro")
    best_f1_weighted = f1_score(best_y_true, best_y_pred, average="weighted")
    best_roc_auc = roc_auc_score(best_y_true, best_probs)
    best_pr_auc = average_precision_score(best_y_true, best_probs)
    best_report = classification_report(
        best_y_true,
        best_y_pred,
        target_names=["safe", "risk"],
        zero_division=0,
        digits=4,
    )
    print("\n===== Best Fold Detailed Classification Report =====")
    print(f"(selected by highest F1, fold = {best_idx+1})")
    print(f"Accuracy:     {best_acc:.4f}")
    print(f"Macro F1:     {best_f1_macro:.4f}")
    print(f"Weighted F1:  {best_f1_weighted:.4f}")
    print(f"ROC AUC:      {best_roc_auc:.4f}")
    print(f"PR AUC (AP):  {best_pr_auc:.4f}")
    print("Confusion matrix (rows=true, cols=pred) [safe(0), risk(1)]:")
    print(best_cm)
    print(best_report)
    out = {
        "fold_metrics": all_metrics,
        "summary": {
            "ROC_AUC_mean": roc_m,
            "ROC_AUC_std": roc_s,
            "PR_AUC_mean": pr_m,
            "PR_AUC_std": pr_s,
            "FNR_mean": fnr_m,
            "FNR_std": fnr_s,
            "decision": args.decision,
            "recall_target": args.recall_target,
            "pos_weight_factor": args.pos_weight_factor,
        },
        "best_fold_eval": {
            "fold": best_idx + 1,
            "accuracy": best_acc,
            "f1_macro": best_f1_macro,
            "f1_weighted": best_f1_weighted,
            "roc_auc": best_roc_auc,
            "pr_auc": best_pr_auc,
            "confusion_matrix": {
                "tn": int(best_cm[0, 0]),
                "fp": int(best_cm[0, 1]),
                "fn": int(best_cm[1, 0]),
                "tp": int(best_cm[1, 1]),
            },
            "classification_report": best_report,
        },
    }
    out_path = Path(args.meta).with_suffix(".ffnn_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved results to: {out_path}")
    idx = np.arange(n_samples)
    inv_map = {0: "safe", 1: "risk"}
    true_label_str = [inv_map.get(int(v), "") for v in oof_true]
    pred_label_str = [inv_map.get(int(v), "") for v in oof_pred]
    if "description" in df_labels.columns:
        desc_col = df_labels["description"]
    else:
        desc_col = pd.Series([None] * n_samples)
    oof_df = pd.DataFrame(
        {
            "idx": idx,
            "description": desc_col,
            "true_label": oof_true,
            "true_label_str": true_label_str,
            "pred_prob": oof_prob,
            "pred_label": oof_pred,
            "pred_label_str": pred_label_str,
        }
    )
    oof_csv_path = out_dir / "oof_predictions.csv"
    oof_df.to_csv(oof_csv_path, index=False)
    print(f"Saved OOF predictions to: {oof_csv_path}")


if __name__ == "__main__":
    main()