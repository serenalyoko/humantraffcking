import pandas as pd
import numpy as np
from sklearn.decomposition import PCA


import matplotlib.pyplot as plt
import torch
import numpy as np
import scipy

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import roc_curve, classification_report, roc_auc_score, precision_recall_curve, auc
import joblib


def train_xgboost_model(X, y, filename):

    X_train,X_test,y_train,y_test = train_test_split(X,y, stratify=y, test_size=0.2, random_state=42)
    print("Logistic Regression Model Training")
    lr = LogisticRegression(max_iter=300,class_weight='balanced',n_jobs=-1)
    lr.fit(X_train,y_train)
    y_pred = lr.predict(X_test)
    y_prob = lr.predict_proba(X_test)[:,1]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["safe", "risk"]))
    print("ROC-AUC:", roc_auc_score(y_test, y_prob))

    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(recall, precision)
    print("PR-AUC:", pr_auc)

    y_true = y_test
    y_prob = lr.predict_proba(X_test)[:,1]  

    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    pos = (y_train ==1).sum()
    neg = (y_train == 0).sum()
    scale_pos_neg = neg/pos

    print("XGBoost Model Training")

    xgb = XGBClassifier(
        objective="binary:logistic",
        tree_method="hist",    
        device="cpu",   
        eval_metric='auc',
        random_state=42
    )


    param_distributions = {
        "n_estimators":[200,400,600],
        "max_depth": [ 4,6,8],
        "learning_rate":[0.05,0.1],
        "subsample":[0.8,1],
        "colsample_bytree":[0.8,1]
    }


    cv = StratifiedKFold(n_splits=3,shuffle=True,random_state=42)

    search = RandomizedSearchCV(
        estimator=xgb,
        param_distributions=param_distributions,
        n_iter=15,
        scoring='roc_auc',
        cv=cv,
        n_jobs=-1,
        verbose=2,
        random_state=42,
        refit=True
    )


    search.fit(X_train,y_train)
    joblib.dump(best_model, f"{filename}_best_xgb_model.pkl")

    print("Best Params:", search.best_params_)
    print("Best CV ROC-AUC:", search.best_score_)


    best_model = search.best_estimator_

    joblib.dump(best_model, f"{filename}_best_xgb_model.pkl")
    print(f"Saved best model to {filename}_best_xgb_model.pkl")

    y_pred_proba = best_model.predict_proba(X_test)[:, 1]
    print("Validation ROC-AUC:", roc_auc_score(y_test, y_pred_proba))

    y_pred = (y_pred_proba > 0.5).astype(int)
    print(classification_report(y_test, y_pred, digits=4))


    y_prob = best_model.predict_proba(X_test)[:,1]  
    y_prob_train = best_model.predict_proba(X_train)[:,1]  
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)


if __name__ == "__main__":
    labelPaths = [
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/balanced_data_bge_m3_1024d.parquet",
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/downsampled_bge_m3_1024d.parquet",
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/Qwen_embedding/balanced_data_with_Qwen_embeddings.parquet,"
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/Qwen_embedding/labeled_jd_downsampled_with_Qwen_embeddings.parquet"]
    embeddingPaths = [
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/balanced_data_bge_m3_1024d.npy",
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/bge-m3_embedding/downsampled_bge_m3_1024d.npy",
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/Qwen_embedding/balanced_data_qwen3_8b.npy",
        "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/Qwen_embedding/labeled_jd_downsampled_qwen3_8b.npy"]
    
    for i in range(len(labelPaths)):
        filename = labelPaths[i].split("/")[-1].replace(".parquet","")
        print(f"\nProcessing {labelPaths[i]}")
        df = pd.read_parquet(labelPaths[i])
        X = np.load(embeddingPaths[i])
        print(X.shape, X.dtype)
        df["label"]= df['label'].apply(lambda x: 0 if x=='safe' else 1)
        y = df["label"].astype(int).values
        train_xgboost_model(X, y, filename)


