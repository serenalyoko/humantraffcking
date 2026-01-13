import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- load & clean ----
df = pd.read_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/eval_safe_risk.csv")

# normalize sample names
df["Sample"] = df["Sample"].str.strip().str.capitalize()  # Balanced / Downsized

# choose which embedding to visualize
embedding_to_use = "bge-m3"   # change to "bge-m3" if you want

df_emb = df[df["Embedding"] == embedding_to_use].copy()

labels_metrics = ["Precision", "recall", "F1"]
num_vars = len(labels_metrics)

# angles for radar
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

def plot_radar_for_group(df_group, title):
    """df_group: rows for one (label, sample) combination, multiple models"""
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

    for _, row in df_group.iterrows():
        model_name = row["Model"]
        values = [row[m] for m in labels_metrics]
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=model_name)
        ax.fill(angles, values, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_metrics)
    ax.set_ylim(0, 1)  # since they are metrics between 0 and 1
    ax.set_title(title, size=13)
    ax.legend(bbox_to_anchor=(1.25, 1.1))
    plt.tight_layout()
    plt.savefig(f"plots/radar_{embedding_to_use}_{title.replace(' ','_')}.png")

# ---- make 4 charts: (safe/risk) x (Balanced/Downsized) ----
for lbl in ["safe", "risk"]:
    for sample in ["Balanced", "Downsized"]:
        subset = df_emb[(df_emb["label"] == lbl) & (df_emb["Sample"] == sample)]
        if subset.empty:
            continue  # skip if this combo doesn't exist
        chart_title = f"{embedding_to_use} — {lbl} — {sample}"
        plot_radar_for_group(subset, chart_title)