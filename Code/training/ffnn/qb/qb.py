import argparse, os, ast, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, \
                            confusion_matrix, precision_score, recall_score

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader


def _parse_vector(v):
    if isinstance(v, np.ndarray):
        return v.astype(np.float32)

    if isinstance(v, (list, tuple)):
        return np.asarray(v, dtype=np.float32)

    if isinstance(v, str):
        v = v.strip()
        try:
            obj = json.loads(v)
        except Exception:
            try:
                obj = ast.literal_eval(v)
            except Exception:
                raise ValueError(f"Cannot parse embedding string: {v[:80]}")
        return np.asarray(obj, dtype=np.float32)

    raise ValueError(f"Unknown embedding type: {type(v)}")


def load_embeddings_and_labels(path):
    df = pd.read_parquet(path)

    if "label" not in df.columns:
        raise ValueError("No label column in file.")

    for cand in ["qwen3_8b", "embedding", "embeddings", "vector", "features"]:
        if cand in df.columns:
            emb_col = cand
            break
    else:
        raise ValueError("No embedding column found (e.g. qwen3_8b)")

    print(f"Detected embedding column: {emb_col}")

    X = np.stack([_parse_vector(v) for v in df[emb_col].tolist()]).astype(np.float32)

    mapping = {"safe": 0, "risk": 1}
    y = df["label"].map(mapping).astype(int).values

    return X, y, df


class FFNN(nn.Module):
    def __init__(self, in_dim, hidden=256, dropout=0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--hidden", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--out_csv", required=True)
    args = parser.parse_args()

    print("Loading data…")
    X, y, df = load_embeddings_and_labels(args.labels)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    class EmbDataset(Dataset):
        def __init__(self, X, y):
            self.X = torch.from_numpy(X).float()
            self.y = torch.from_numpy(y).float()

        def __len__(self):
            return len(self.X)

        def __getitem__(self, i):
            return self.X[i], self.y[i]

    ds = EmbDataset(X, y)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True)

    model = FFNN(in_dim=X.shape[1], hidden=args.hidden, dropout=args.dropout).to(device)
    pos_ratio = (y == 1).mean()
    neg_ratio = 1 - pos_ratio
    pos_weight = torch.tensor([neg_ratio / pos_ratio], device=device)
    loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)

    print("Training model…")
    for ep in range(1, args.epochs + 1):
        model.train()
        total_loss = 0
        for xb, yb in dl:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total_loss += loss.item() * len(xb)
        print(f"Epoch {ep:02d} | loss={total_loss/len(ds):.4f}")

    print("Predicting on all samples…")
    model.eval()
    with torch.no_grad():
        probs = torch.sigmoid(
            model(torch.from_numpy(X).float().to(device))
        ).cpu().numpy()

    preds = (probs >= 0.5).astype(int)

    if "description" in df.columns:
        desc_col = df["description"]
    else:
        desc_col = pd.Series([None] * len(df))

    out_df = pd.DataFrame({
        "description": desc_col,
        "true_label": y,
        "pred_prob": probs,
        "pred_label": preds
    })

    out_df.to_csv(args.out_csv, index=False)
    print(f"\n Saved predictions to: {args.out_csv}")


if __name__ == "__main__":
    main()