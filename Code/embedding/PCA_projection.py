import ast
from os import path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.lines import Line2D

# ---------- 3) Convert qwen3_8b -> 2D numpy array ----------
def to_array(x):
    """
    x may already be a list/np.array. If it's a string like "[0.1, ...]",
    parse it. Returns np.ndarray or None if it fails.
    """
    if isinstance(x, np.ndarray):
        return x
    if isinstance(x, (list, tuple)):
        return np.asarray(x)
    if isinstance(x, str):
        try:
            return np.asarray(ast.literal_eval(x))
        except Exception:
            return None
    return None

def plot_PCA(df, outname):
    # Keep only rows that have both an embedding and a label
    df = df.dropna(subset=["embedding", "label"]).reset_index(drop=True)

    # ---------- 2) Normalize label column ----------
    # map to numeric: safe -> 0 (blue), risk -> 1 (red)
    norm_label = df["label"].astype(str).str.strip().str.lower()
    label_map = {"safe": 0, "risk": 1, "0": 0, "1": 1}
    labels = norm_label.map(label_map)

    # Drop rows with unknown labels (if any)
    mask_known = labels.notna()
    if mask_known.sum() < len(df):
        print(f"Dropping {len(df) - mask_known.sum()} rows with unknown labels:", 
            sorted(df.loc[~mask_known, "label"].unique()))
    df = df.loc[mask_known].reset_index(drop=True)
    labels = labels.loc[mask_known].astype(int).to_numpy()

    vecs = df["embedding"].apply(to_array)

    # Drop rows that didn't parse into numeric vectors or have inconsistent dims
    lens = vecs.apply(lambda v: v.shape[0] if isinstance(v, np.ndarray) and v.ndim == 1 else -1)
    mode_dim = lens[lens > 0].mode().iloc[0]  # most common embedding length
    good = lens.eq(mode_dim)

    if good.sum() < len(df):
        print(f"Dropping {len(df) - good.sum()} rows with bad/missing vectors or wrong dim "
            f"(expected {mode_dim}).")

    vecs = vecs[good]
    labels = labels[good.to_numpy()]

    embeddings = np.vstack(vecs.values).astype(np.float32)
    print("Embeddings shape:", embeddings.shape, "Labels shape:", labels.shape)

    # ---------- 4) PCA ----------
    pca = PCA(n_components=2, random_state=42)
    emb_2d = pca.fit_transform(embeddings)
    print("Explained variance ratio (PC1, PC2):", pca.explained_variance_ratio_)

    # ---------- 5) Plot (safe=blue, risk=red) ----------
    label_to_color = {0: "blue", 1: "red"}
    node_colors = [label_to_color[int(l)] for l in labels]

    plt.figure(figsize=(8, 6))
    plt.scatter(emb_2d[:, 0], emb_2d[:, 1], c=node_colors, s=20, alpha=0.7, edgecolors="none")
    plt.title("PCA Projection (Safe vs Risk)")
    plt.xlabel("PC1"); plt.ylabel("PC2")

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Safe', markerfacecolor='blue', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Risk', markerfacecolor='red', markersize=8),
    ]
    plt.legend(handles=legend_elements, title="Label")
    plt.tight_layout()
    plt.savefig(f"plots/{outname}.png", dpi=300)
    #plt.show()


def plot_PCA_3D(df, outname):
    labels = df["label"].astype(str).str.strip().str.lower().map({"safe":0,"risk":1,"0":0,"1":1}).astype(int)
    vecs = df["embedding"].apply(to_array)
    dims = vecs.apply(lambda v: v.shape[0] if isinstance(v,np.ndarray) and v.ndim==1 else -1)
    mode_dim = dims[dims>0].mode().iloc[0]
    good = dims.eq(mode_dim)
    embeddings = np.vstack(vecs[good].values).astype(np.float32)
    labels = labels[good]

    # --- PCA to 3D ---
    pca3 = PCA(n_components=3, random_state=42)
    emb_3d = pca3.fit_transform(embeddings)
    print("Explained variance ratio (PC1, PC2, PC3):", pca3.explained_variance_ratio_)

    # --- Plot 3D ---
    label_to_color = {0:"blue", 1:"red"}
    colors = [label_to_color[int(l)] for l in labels]

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(emb_3d[:,0], emb_3d[:,1], emb_3d[:,2], c=colors, s=20, alpha=0.7, edgecolors="none")

    ax.set_title("3D PCA Projection (Safe vs Risk)")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.set_zlabel("PC3")

    legend_elements = [
        Line2D([0],[0], marker='o', color='w', label='Safe', markerfacecolor='blue', markersize=8),
        Line2D([0],[0], marker='o', color='w', label='Risk', markerfacecolor='red', markersize=8),
    ]
    ax.legend(handles=legend_elements, title="Label")

    plt.tight_layout()
    plt.savefig(f"plots/{outname}_3D.png", dpi=300)
    plt.show()
# ---------- 1) Load ----------
paths = ["Data/Qwen_embedding/balanced_data_with_Qwen_embeddings.parquet",
         "Data/Qwen_embedding/labeled_jd_downsampled_with_Qwen_embeddings.parquet",
         "Data/bge-m3_embedding/labeled_jd_downsampled_bge_m3_1024d.parquet"]
for path in paths:
    df = pd.read_parquet(path)  # needs pyarrow or fastparquet
    print(df.columns)
    df.columns = [re.sub(r"qwen3_8b", "embedding", col) for col in df.columns]
    outname = path.split("/")[-1].replace(".parquet", "")
    plot_PCA_3D(df, outname)

