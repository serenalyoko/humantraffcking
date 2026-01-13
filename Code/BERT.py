# finetune_distilbert_on_custom_embeds.py
import os, copy, numpy as np, pyarrow.parquet as pq
from sklearn.model_selection import train_test_split

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from transformers import DistilBertForSequenceClassification
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve, average_precision_score, precision_recall_curve
)
# ---------------------------
# Config
# ---------------------------
EMB_COL = "embedding_768"     # change to your column name
LABEL_COL = "label"          # string labels "safe"/"risk" or 0/1
NUM_CLASSES = 2
BATCH_SIZE = 16
EPOCHS = 10
LR = 2e-5
SEED = 42

LABEL_MAP = {"safe": 0, "risk": 1}  # tweak if your labels differ

# ---------------------------
# Dataset / Collator
# ---------------------------
class EmbeddingDataset(Dataset):
    """
    Expects:
      X: np.ndarray shape (N, 768) float32
      y: np.ndarray shape (N,)   int64 (class ids)
    Yields one sentence-level embedding per sample.
    """
    def __init__(self, X, y):
        assert X.ndim == 2 and X.shape[1] == 768, "Embeddings must be (N, 768)"
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self): 
        return self.X.shape[0]

    def __getitem__(self, idx):
        return {
            # keep as (768,) here; collate will add seq_len=1 dimension
            "emb": self.X[idx],
            "label": self.y[idx]
        }

def collate_embedded(batch):
    # Stack to (batch, 1, 768) and build attention_mask of ones
    embs = torch.stack([b["emb"] for b in batch], dim=0).unsqueeze(1)  # (B, 1, 768)
    mask = torch.ones(embs.size(0), 1, dtype=torch.long)               # (B, 1)
    labels = torch.stack([b["label"] for b in batch], dim=0)           # (B,)
    return {"inputs_embeds": embs, "attention_mask": mask, "labels": labels}

# ---------------------------
# Data prep
# ---------------------------
def load_parquet_embeddings(path, emb_col=EMB_COL, label_col=LABEL_COL):
    table = pq.read_table(path, columns=[emb_col, label_col])
    # Convert column of lists -> np.array
    emb_col_py = [np.array(v, dtype=np.float32) for v in table[emb_col].to_pylist()]
    X = np.stack(emb_col_py, axis=0)  # (N, 768)

    labels_py = table[label_col].to_pylist()
    # Convert string labels to ids if needed
    if isinstance(labels_py[0], str):
        y = np.array([LABEL_MAP[l] for l in labels_py], dtype=np.int64)
    else:
        y = np.array(labels_py, dtype=np.int64)

    return X, y

def make_loaders(X, y, batch_size=BATCH_SIZE, seed=SEED):
    X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
    X_dev, X_te, y_dev, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=seed, stratify=y_tmp)
    train_ds = EmbeddingDataset(X_tr, y_tr)
    dev_ds   = EmbeddingDataset(X_dev, y_dev)
    test_ds  = EmbeddingDataset(X_te, y_te)
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  collate_fn=collate_embedded)
    dev_dl   = DataLoader(dev_ds,   batch_size=batch_size, shuffle=False, collate_fn=collate_embedded)
    test_dl  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False, collate_fn=collate_embedded)
    return train_dl, dev_dl, test_dl

# ---------------------------
# Training
# ---------------------------
def finetune_distilbert_on_embeds(model, train_dl, dev_dl, device, filename):
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    best_loss = float("inf")
    best_state = None

    total_steps = EPOCHS * len(train_dl)
    with tqdm(total=total_steps, desc="Finetuning:") as pbar:
        for epoch in range(EPOCHS):
            model.train()
            tr_loss = 0.0
            for batch in train_dl:
                batch = {k: v.to(device) for k, v in batch.items()}

                optimizer.zero_grad()
                out = model(**batch)  # uses built-in CE loss
                loss = out.loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                tr_loss += loss.item()
                pbar.update(1)

            tr_loss /= max(1, len(train_dl))
            print(f"Epoch {epoch}: train loss = {tr_loss:.6f}")

            # ---- eval ----
            model.eval()
            dev_loss = 0.0
            with torch.no_grad():
                for batch in dev_dl:
                    batch = {k: v.to(device) for k, v in batch.items()}
                    out = model(**batch)
                    dev_loss += out.loss.item()
            dev_loss /= max(1, len(dev_dl))
            print(f"Epoch {epoch}: dev loss = {dev_loss:.6f}")

            if dev_loss < best_loss:
                best_loss = dev_loss
                best_state = copy.deepcopy(model.state_dict())
                torch.save(best_state, f"{filename}_best_model.pt")
                print(f"Best dev loss {dev_loss:.6f} — checkpoint saved to best_model.pt")

    if best_state is not None:
        model.load_state_dict(best_state)
    return f"{filename}_best_model.pt"

def evaluate_model(model, test_dl, device, class_names=("safe","risk")):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []

    for batch in test_dl:
        batch = {k: v.to(device) for k, v in batch.items()}
        out = model(**batch)
        logits = out.logits                       # (B, 2)
        probs  = torch.softmax(logits, dim=1)[:,1]# P(class=1="risk")
        preds  = torch.argmax(logits, dim=1)

        all_probs.extend(probs.detach().cpu().numpy())
        all_preds.extend(preds.detach().cpu().numpy())
        all_labels.extend(batch["labels"].cpu().numpy())

    all_labels = np.asarray(all_labels)
    all_preds  = np.asarray(all_preds)
    all_probs  = np.asarray(all_probs)

    # Standard metrics
    acc        = accuracy_score(all_labels, all_preds)
    f1_macro   = f1_score(all_labels, all_preds, average="macro")
    f1_weighted= f1_score(all_labels, all_preds, average="weighted")
    cm         = confusion_matrix(all_labels, all_preds, labels=[0,1])
    report     = classification_report(all_labels, all_preds, target_names=list(class_names))

    # ROC / AUC
    auc_roc    = roc_auc_score(all_labels, all_probs)         # scalar
    fpr, tpr, roc_th = roc_curve(all_labels, all_probs)       # arrays

    # PR / AP (often more informative for imbalance)
    ap_pr      = average_precision_score(all_labels, all_probs)
    prec, rec, pr_th = precision_recall_curve(all_labels, all_probs)

    print(f"Accuracy:     {acc:.4f}")
    print(f"Macro F1:     {f1_macro:.4f}")
    print(f"Weighted F1:  {f1_weighted:.4f}")
    print(f"ROC AUC:      {auc_roc:.4f}")
    print(f"PR AUC (AP):  {ap_pr:.4f}")
    print("Confusion matrix (rows=true, cols=pred) [safe(0), risk(1)]:\n", cm)
    print(report)

    return {
        "accuracy": acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "roc_auc": auc_roc,
        "pr_auc": ap_pr,
        "roc_curve": (fpr, tpr, roc_th),
        "pr_curve": (prec, rec, pr_th),
        "confusion_matrix": cm,
        "report": report,
    }
# ---------------------------
# Main
# ---------------------------

if __name__ == "__main__":
    torch.manual_seed(SEED)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # DistilBertForSequenceClassification will accept inputs_embeds (B, L, 768).
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert/distilbert-base-uncased",
        num_labels=NUM_CLASSES
    ).to(device)

    # (Optional) The input embedding table isn’t used when passing inputs_embeds.
    # You can freeze it to save memory/compute:
    for p in model.distilbert.embeddings.word_embeddings.parameters():
        p.requires_grad = False

    paths = [
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/balanced_projection.parquet",
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/downsampled_projection.parquet",
    ]
    # Print first couple rows of the parquet file
    #table = pq.read_table("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/balanced_projection.parquet")
    #print(table.slice(0, 2).to_pandas())

    trained_weights = ["/Users/d22admin/Documents/human-trafficking/ContentAnalysis/balanced_with_Qwen_project_768_best_model.pt",
                       "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/downsample_with_Qwen_project_768_best_model.pt"]
    

    for i in range(len(paths)):
        print(f"\nProcessing dataset: {paths[i]}")
        X, y = load_parquet_embeddings(paths[i], EMB_COL, LABEL_COL)
        train_dl, dev_dl, test_dl = make_loaders(X, y)
        filename = paths[i].split("/")[-1].split(".")[0]
        best = finetune_distilbert_on_embeds(model, train_dl, dev_dl, device, filename)
        print(f"Finetuning complete. Best model saved to {best}")
        model.load_state_dict(torch.load(best, map_location=device))  # your code already saved best
        evaluate_model(model, test_dl, device)

        