import joblib
import numpy as np
import os
import pandas as pd

from transformers import DistilBertForSequenceClassification
import torch
import pyarrow.parquet as pq
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
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
from torch import nn

# ---- same config as training ----
EMB_COL   = "embedding_768"     # default embedding column name (fallback)
NUM_CLASSES = 2
LABEL_MAP = {"safe": 0, "risk": 1}
ID2LABEL = {v: k for k, v in LABEL_MAP.items()}

BATCH_SIZE = 16
SEED = 42

torch.manual_seed(SEED)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Recreate the same model architecture (DistilBERT)
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert/distilbert-base-uncased",
    num_labels=NUM_CLASSES
).to(device)


class EmbeddingDataset(Dataset):
    """
    Expects:
      X: np.ndarray shape (N, D) float32
      y: np.ndarray shape (N,)   int64 (class ids)
    Yields one sentence-level embedding per sample.
    """
    def __init__(self, X, y):
        assert X.ndim == 2, "Embeddings must be (N, D)"
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self): 
        return self.X.shape[0]

    def __getitem__(self, idx):
        return {
            "emb": self.X[idx],
            "label": self.y[idx]
        }


class UnlabeledEmbeddingDataset(Dataset):
    """
    X: np.ndarray of shape (N, D) float32
    """
    def __init__(self, X):
        assert X.ndim == 2
        self.X = torch.tensor(X, dtype=torch.float32)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return {"emb": self.X[idx]}


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


def collate_embedded_infer(batch):
    # Stack to (B, 1, D) and build attention_mask of ones
    embs = torch.stack([b["emb"] for b in batch], dim=0).unsqueeze(1)  # (B, 1, D)
    mask = torch.ones(embs.size(0), 1, dtype=torch.long)               # (B, 1)
    return {"inputs_embeds": embs, "attention_mask": mask}


def load_parquet_embeddings_unlabeled(path, emb_col=EMB_COL):
    """
    Utility function (not used in label() anymore, but kept if needed elsewhere).
    """
    table = pq.read_table(path, columns=[emb_col])
    emb_col_py = [np.array(v, dtype=np.float32) for v in table[emb_col].to_pylist()]
    X = np.stack(emb_col_py, axis=0)  # (N, D)
    return X


def label_with_bert(modelFilePath, embeddings, batch_size=32):
    """
    Use DistilBERT classifier on precomputed embeddings passed as a numpy array.
    """
    state_dict = torch.load(
        modelFilePath,
        map_location=device
    )
    model.load_state_dict(state_dict)
    model.eval()

    X = np.asarray(embeddings, dtype=np.float32)
    ds = UnlabeledEmbeddingDataset(X)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False,
                    collate_fn=collate_embedded_infer)

    all_pred_ids = []
    all_pred_labels = []
    all_pred_probs = []
    all_probs = []

    with torch.no_grad():
        for batch in dl:
            batch = {k: v.to(device) for k, v in batch.items()}
            out = model(**batch)
            logits = out.logits                        # (B, NUM_CLASSES)
            probs = F.softmax(logits, dim=1)           # (B, NUM_CLASSES)

            confs, pred_ids = torch.max(probs, dim=1)  # (B,)
            pred_ids = pred_ids.cpu().numpy()
            confs = confs.cpu().numpy()
            probs_np = probs.cpu().numpy()

            labels = [ID2LABEL[int(i)] for i in pred_ids]

            all_pred_ids.extend(pred_ids)
            all_pred_probs.extend(confs)
            all_pred_labels.extend(labels)
            all_probs.append(probs_np)

    all_probs = np.vstack(all_probs)  # (N, NUM_CLASSES)
    return (
        np.array(all_pred_ids),
        all_pred_labels,
        np.array(all_pred_probs),
        all_probs,
    )


def label_with_xgb(filePath, embeddings):
    best_model = joblib.load(filePath)
    embeddings = np.asarray(embeddings, dtype=np.float32)
    probs = best_model.predict_proba(embeddings)         # (N, 2)
    probs_risk = probs[:, 1]                             # P(y=1 | message)
    preds = best_model.predict(embeddings)               # 0 or 1 per row

    label_map = {0: "safe", 1: "risk"}
    pred_labels = np.vectorize(label_map.get)(preds)
    return pred_labels, probs_risk


def label_with_ffnn(model_path, embeddings, device=device):
    embeddings = np.asarray(embeddings, dtype=np.float32)
    input_dim = embeddings.shape[1]

    # model with single-output head (matches training)
    model_ffnn = FFNN(in_dim=input_dim, hidden=256)
    state_dict = torch.load(model_path, map_location=device)
    model_ffnn.load_state_dict(state_dict)

    model_ffnn.to(device)
    model_ffnn.eval()

    with torch.no_grad():
        inputs = torch.tensor(embeddings, dtype=torch.float32).to(device)
        logits = model_ffnn(inputs).squeeze(-1)    # (N,)
        probs_risk = torch.sigmoid(logits).cpu().numpy()  # P(y=1 | x)

    # threshold at 0.5 to get predicted class
    preds = (probs_risk >= 0.5).astype(int)       # 0 or 1

    label_map = {0: "safe", 1: "risk"}
    pred_labels = np.vectorize(label_map.get)(preds)

    return pred_labels, probs_risk


def label(modelsPath, dataPath, embedding, projection=False):
    """
    modelsPath: directory that contains model files
    dataPath:  parquet path with embeddings
    embedding: substring used to select the right models (e.g., "bge_m3_1024d")
    projection: if True, use BERT models; else use XGB/FFNN
    """
    data_df = pd.read_parquet(dataPath)

    # try to pick a reasonable embedding column
    if "embedding" in data_df.columns:
        emb_col = "embedding"
    elif "qwen3_8b" in data_df.columns:
        emb_col = "qwen3_8b"
    elif "embedding_768" in data_df.columns:
        emb_col = "embedding_768"
    elif "qwen3_8b_768" in data_df.columns:
        emb_col = "qwen3_8b_768"

    emb_list = data_df[emb_col].tolist()
    X = np.stack(emb_list, axis=0)  # (N, D)

    models = os.listdir(modelsPath)
    model_results = {}

    for model_file in models:
        full_path = os.path.join(modelsPath, model_file)
        #print(f"{model_file} \n {dataPath} \n projection: {projection}")
        if "xgb" in model_file and embedding in model_file and not projection:
            print("\n Predicting with XGB model:", model_file, "\n with embedding:", dataPath)
            pred_labels, probs_risk = label_with_xgb(full_path, X)
            model_results[model_file] = (pred_labels, probs_risk)

        elif "bert" in model_file.lower() and (embedding in model_file) and projection==True:
            print("\n Predicting with BERT model:", model_file, "\n with embedding:", dataPath)
            pred_ids, pred_labels, pred_probs, all_probs = label_with_bert(
                full_path, X, batch_size=32
            )
            model_results[model_file] = (pred_labels, pred_probs)

        elif "ffnn" in model_file and embedding in model_file and not projection:
            print("\n Predicting with FFNN model:", model_file, "\n with embedding:", dataPath)
            pred_labels, probs_risk = label_with_ffnn(full_path, X)
            model_results[model_file] = (pred_labels, probs_risk)
    
    """
    model_results: { model_filename: (pred_labels, probs_array) }
    """
    return model_results


def combine_model_results(model_results, N):
    """
    model_results structure:
      {
        "Qwen": { model_name: (pred_labels, probs_risk), ... },
        "bge":  { model_name: (pred_labels, probs_risk), ... }
      }
    """
    decision = []
    decision_confidence = []

    total_models = sum(len(mdict) for mdict in model_results.values())
    majority = total_models // 2 + 1 if total_models > 0 else 1

    for i in range(N):
        risk_votes = 0
        confidences = []

        for embedding_key, models in model_results.items():
            for model_name, (labels, probs) in models.items():
                confidences.append(probs[i])
                if labels[i] == "risk":
                    risk_votes += 1

        if confidences:
            confidence_interval = (min(confidences), max(confidences))
        else:
            confidence_interval = (0.0, 0.0)

        decision_confidence.append(confidence_interval)

        if risk_votes >= majority:
            decision.append("risk")
        else:
            decision.append("safe")

    return decision, decision_confidence
        


if __name__ == "__main__":
    dataPath_bge = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/all_data_embedding/combined_job_data_df_embedding_bge_m3_1024d.parquet"
    dataPath_Qwen = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/all_data_embedding/combined_job_data_df_embedding_with_Qwen_embeddings.parquet"
    dataPath_bge_768 = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/all_data_embedding/combined_job_data_df_embedding_bge_768.parquet"
    dataPath_QWen_768 = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/all_data_embedding/combined_job_data_df_embedding_Qwen_768.parquet"

    # map embedding names to their parquet paths
    embedding_to_parquet = {
        "bge_m3_1024d": dataPath_bge,
        "Qwen_1024d": dataPath_Qwen,
        "bge_768": dataPath_bge_768,
        "Qwen_768": dataPath_QWen_768,
    }

    embeddings = ["bge_m3_1024d", "Qwen_1024d", "bge_768", "Qwen_768"]

    modelsPath  = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/models"
    dataPath = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_3.0.csv"
    data = pd.read_csv(dataPath)

    all_model_results = {}
    for embeddingName in embeddings:
        embedding_key = "Qwen" if "Qwen" in embeddingName else "bge"
        parquet_path = embedding_to_parquet[embeddingName]

        model_results = label(
            modelsPath,
            parquet_path,
            embedding_key,
            projection=("768" in parquet_path)
        )

        if embedding_key not in all_model_results:
            all_model_results[embedding_key] = {}
        for model_file, result in model_results.items():
            all_model_results[embedding_key][model_file] = result
    
    decision, decision_confidence = combine_model_results(all_model_results, len(data))
    data["Our_Model_label"] = decision
    data["Our_Model_confidence"] = decision_confidence
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_4.0.csv"
    data.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved labeled data to: {output_path}")
