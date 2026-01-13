import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)

def _to_binary(series, positive="risk"):
    """
    Convert a label/pred column to binary {0,1} with 'risk' as the positive class by default.
    Handles strings like 'risk'/'safe', '1'/'0', booleans, and ints.
    """
    def norm(x):
        if isinstance(x, str):
            x = x.strip().lower()
            if x in {"1", "true", "yes"}: return 1
            if x in {"0", "false", "no"}: return 0
            if x == positive: return 1
            if x in {"safe", "negative", "neg"}: return 0
            # last resort: try casting
            try:
                return int(float(x))
            except:
                return np.nan
        if isinstance(x, (int, np.integer, float, np.floating)):
            return int(x)
        if isinstance(x, bool):
            return int(x)
        return np.nan

    out = series.map(norm)
    return out.astype("float")  # keep float for potential NaN, cast later after dropna

def evaluate_zero_shot(
    df: pd.DataFrame,
    true_col: str = "label",
    pred_col: str = "Qwen3-0.6B_label",
    score_col: str | None = None,
    positive_label: str = "risk"
):
    """
    Computes accuracy, precision, recall, F1, AUC, and ROC points.
    If score_col is None, tries to auto-detect a score/prob column.
    Returns a results dict and (fpr, tpr, thresholds).
    """

    # Auto-detect a score column if not provided
    if score_col is None:
        for cand in [f"{pred_col}_score", f"{pred_col}_prob", f"{pred_col}_prob_{positive_label}", "score", "prob", "prob_risk"]:
            if cand in df.columns:
                score_col = cand
                break

    y_true = _to_binary(df[true_col], positive=positive_label)
    y_pred = _to_binary(df[pred_col], positive=positive_label)

    # Drop rows with missing values in required columns
    needed = [y_true, y_pred]
    if score_col and score_col in df.columns:
        y_score_raw = df[score_col]
        needed.append(y_score_raw)
        valid = ~pd.concat(needed, axis=1).isna().any(axis=1)
        y_score = y_score_raw[valid].astype(float)
    else:
        valid = ~pd.concat(needed, axis=1).isna().any(axis=1)
        y_score = None

    y_true = y_true[valid].astype(int)
    y_pred = y_pred[valid].astype(int)

    # Metrics from hard predictions
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    # AUC & ROC
    # Prefer true scores if available; otherwise use y_pred (degenerate ROC with two points).
    if y_score is not None:
        auc = roc_auc_score(y_true, y_score)
        fpr, tpr, thr = roc_curve(y_true, y_score)
        score_used = score_col
    else:
        # Fall back to using hard labels (will produce a step function with 2 thresholds)
        auc = roc_auc_score(y_true, y_pred)
        fpr, tpr, thr = roc_curve(y_true, y_pred)
        score_used = "(hard labels only)"

    report = classification_report(
        y_true, y_pred,
        target_names=[f"not-{positive_label}", positive_label],
        zero_division=0,
        digits=4
    )

    results = {
        "n_samples": int(len(y_true)),
        "positive_class": positive_label,
        "score_used": score_used,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "auc": auc,
        "confusion_matrix": {
            "tn": int(cm[0,0]), "fp": int(cm[0,1]),
            "fn": int(cm[1,0]), "tp": int(cm[1,1])
        },
        "classification_report": report
    }
    return results, (fpr, tpr, thr)

# ---- Example usage ----
#paths = ["/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/balanced_data_zeroshot_Qwen3-0.6B_labels.csv",
#         "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd_downsampled_zeroshot_Qwen3-0.6B_labels.csv"]

paths = ["/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/zero_shot_result_DeepSeek.pkl",
         "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/zero_shot_result_gemini_refined.pkl"]
    
for path in paths:
    #print(f"Qwen3-0.6B {path.split('/')[-1]}:")
    #df = pd.read_csv(path)
    print(f"Results from {path.split('/')[-1]}:")
    with open(path, "rb") as f:
        df = pickle.load(f)
    #print(df)
    if "DeepSeek" in path:
        pred_col = "deepseek_zeroshot"
    if "gemini_" in path:
        pred_col = "gemini_zeroshot"
    results, (fpr, tpr, thr) = evaluate_zero_shot(df,
                                                true_col="label",
                                                pred_col=pred_col)
    #     # score_col="Qwen3-0.6B_prob_risk"  # uncomment if you have probs

    print(results["classification_report"])
    print({k: round(results[k], 4) for k in ["accuracy", "precision", "recall", "f1", "auc"]})