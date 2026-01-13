import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ----------------- Load & clean data -----------------
df = pd.read_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/eval_safe_risk.csv")

df["Sample"] = df["Sample"].str.strip().str.capitalize()

model_order = [
    "Logistic regression",
    "Logistic regression + XGBoost",
    "FFNN",
    "DistilBERT"
]
model_order = [m for m in model_order if m in df["Model"].unique()]
model_to_y = {m: i for i, m in enumerate(model_order)}

embeddings = df["Embedding"].unique()
embedding_colors = {
    emb: color for emb, color in zip(embeddings, ["tab:blue", "tab:orange", "tab:green", "tab:red"])
}

sample_markers = {
    "Balanced": "o",
    "Downsized": "^"
}

# ----------------- Plot -----------------
labels = ["safe", "risk"]
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

for ax, lbl in zip(axes, labels):
    sub = df[df["label"] == lbl]

    for _, row in sub.iterrows():
        model = row["Model"]
        if model not in model_to_y:
            continue

        y = model_to_y[model]
        x = row["F1"]
        emb = row["Embedding"]
        sample = row["Sample"]

        ax.scatter(
            x,
            y,
            s=60,
            marker=sample_markers.get(sample, "o"),
            color=embedding_colors.get(emb, "black"),
            edgecolor="black",
            linewidth=0.7,
            alpha=0.9
        )

    ax.set_title(f"Label: {lbl}", fontsize=13)
    ax.set_xlabel("F1", fontsize=11)
    ax.set_xlim(0.6, 1.0)
    ax.set_yticks(list(model_to_y.values()))
    ax.set_yticklabels(model_order)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

# ----------------- LEGENDS -----------------
from matplotlib.lines import Line2D

# Embedding color legend
embedding_handles = [
    Line2D([0], [0], marker="o", color="none",
           markerfacecolor=embedding_colors[e], markeredgecolor="black",
           markersize=8, label=e)
    for e in embeddings
]

# Sampling marker legend
sample_handles = [
    Line2D([0], [0], marker=sample_markers[s], color="black",
           markerfacecolor="lightgray", markersize=8, label=s)
    for s in sample_markers.keys()
]

# Add the color legend to the RIGHT subplot
legend1 = axes[1].legend(handles=embedding_handles, title="Embedding",
                         bbox_to_anchor=(1.02, 1.0), loc="upper left")

# Add the marker legend *after*, so it doesn’t overwrite the first legend
axes[1].add_artist(legend1)   # <-- IMPORTANT FIX

axes[1].legend(handles=sample_handles, title="Sample",
               bbox_to_anchor=(1.02, 0.55), loc="upper left")

plt.tight_layout()
fig.savefig("plots/cleveland_dotplot_f1.png", dpi=300, bbox_inches="tight")