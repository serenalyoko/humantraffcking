import pandas as pd
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import geopandas as gpd
from geodatasets import get_path
import numpy as np
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt
STATES_URL = "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip"

def eval_our_model(valid_pairs):
    y_true = [o for o, u in valid_pairs]
    y_pred = [u for o, u in valid_pairs]

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

def label_count(ls, labels):
    label_counts = {}
    for i in range(len(ls)):
        jt = ls[i]
        label = labels[i]
        if jt not in label_counts:
            label_counts[jt] = {"safe": 0, "risk": 0}
        label_counts[jt][label] += 1
    normalized_counts = {}
    for key in label_counts.keys():
        total = label_counts[key]["safe"] + label_counts[key]["risk"]
        normalized_counts[key] = {
            "safe": label_counts[key]["safe"] / total if total > 0 else 0,
            "risk": label_counts[key]["risk"] / total if total > 0 else 0
        }
    
    return label_counts, normalized_counts

def get_label_counts(df):
    job_type = df["job type"].tolist()
    location = df["location"].tolist()
    contact_method = df["contact method"].tolist()
    gender_preference = df["gender preference"].tolist()
    our_labels = df["Our_Model_label"].tolist()
    jt_counts, jt_normalized = label_count(job_type, our_labels)
    loc_counts, loc_normalized = label_count(location, our_labels)
    cm_counts, cm_normalized  = label_count(contact_method, our_labels)
    gp_counts, gp_normalized  = label_count(gender_preference, our_labels)
    res = {"job_type": {"count":jt_counts, "normalized": jt_normalized},
           "location": {"count":loc_counts, "normalized": loc_normalized},
           "contact_method": {"count":cm_counts, "normalized": cm_normalized},
           "gender_preference": {"count":gp_counts, "normalized": gp_normalized}}
    for key in res.keys():
        df_prep = {"category": [], "safe": [], "risk": [],"normalized_safe": [], "normalized_risk": []}
        for cat in res[key]["count"].keys():
            df_prep["category"].append(cat)
            df_prep["safe"].append(res[key]["count"][cat]["safe"])
            df_prep["risk"].append(res[key]["count"][cat]["risk"])
            df_prep["normalized_safe"].append(res[key]["normalized"][cat]["safe"])
            df_prep["normalized_risk"].append(res[key]["normalized"][cat]["risk"])
        df_out = pd.DataFrame(df_prep)
        df_out.to_csv(f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/analysis/{key}_label_counts.csv", index=False)
    return res

def plot(key_dict, title, out, xlabel):
    labels = list(key_dict.keys())
    safe_vals = [key_dict[k]["safe"] for k in labels]
    risk_vals = [key_dict[k]["risk"] for k in labels]

    x = range(len(labels))
    plt.figure(figsize=(9, 6))
    plt.barh(x, risk_vals, height=0.4, label='Risk', color='r', align='center')

    plt.barh(x, safe_vals, height=0.4, left=risk_vals,label='Safe', color='b', align='center')
    plt.yticks(x, labels, rotation=0)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()


def plot_map(states_dict, title, out, xlabel):
    """
    states_dict: {"California": {"safe": X, "risk": Y}, ...}
    """

    # 1. Load US states shapefile
    gdf = gpd.read_file(STATES_URL)

    # Remove territories
    territories = ["American Samoa", "Guam", "Northern Mariana Islands",
                   "Puerto Rico", "United States Virgin Islands", "Alaska", "Hawaii"]
    gdf = gdf[~gdf["NAME"].isin(territories)].copy()

    # 2. Convert your dict to a DataFrame
    data = []
    output = {"state":[], "risk_val":[],"total":[], "proportion":[]}
    for state_name, vals in states_dict.items():
        safe = vals.get("safe", 0)
        risk = vals.get("risk", 0)
        total = safe + risk

        if xlabel.lower() == "count":
            value = risk
        else:  # Proportion
            value = risk / total if total > 0 else np.nan
        data.append({"NAME": state_name, "risk_val": value})

        output["state"].append(state_name)
        output["risk_val"].append(risk) 
        output["total"].append(total)
        output["proportion"].append(value)
    output_df = pd.DataFrame(output)
    output_df.to_csv(f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/{xlabel.replace(' ','_').lower()}_by_state.csv", index=False)
    df_risk = pd.DataFrame(data)

    # 3. Merge state shapes with risk values
    gdf = gdf.merge(df_risk, on="NAME", how="left")

    # 4. Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(
        column="risk_val",
        cmap="Reds",
        legend=True,
        edgecolor="black",
        linewidth=0.5,
        ax=ax
    )

    # Annotate each state with its risk_val using adjustText to avoid overlap
    from adjustText import adjust_text
    texts = []
    for idx, row in gdf.iterrows():
        if pd.notnull(row["risk_val"]):
            x, y = row["geometry"].centroid.coords[0]
            risk_val = row["risk_val"]
            cmap = plt.get_cmap("Reds")
            norm = plt.Normalize(gdf["risk_val"].min(), gdf["risk_val"].max())
            rgba = cmap(norm(risk_val))
            r, g, b = rgba[:3]
            brightness = (r*0.299 + g*0.587 + b*0.114)
            text_color = "black" if brightness > 0.6 else "white"
            texts.append(
                ax.text(
                    x, y, f"{risk_val:.2f}",
                    color=text_color,
                    fontsize=5,
                    ha="center",
                    va="center"
                )
            )
    adjust_text(
        texts,
        ax=ax,
        expand_text=(0, 0),
        arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, shrinkA=10)
    )

    ax.set_title(title, fontsize=14)
    ax.set_axis_off()

    # Adjust colorbar label
    cbar = ax.get_figure().axes[-1]
    cbar.set_ylabel(xlabel)

    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()

def plot_all(df):
    counts = get_label_counts(df)
    for col in counts.keys():
        if col == "location":
            plot_map(counts[col]["count"],
                     title=f"Risk Ads Count by {col.replace('_',' ').title()}",
                     out=f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/{col}_label_count_map.png",
                     xlabel="Count")

            plot_map(counts[col]["normalized"],
                     title=f"Normalized Risk Ads Distribution by {col.replace('_',' ').title()}",
                     out=f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/{col}_label_distribution_map.png",
                     xlabel="Proportion")
            print(counts[col]["count"]["Not specified"])
            print(counts[col]["normalized"]["Not specified"])
        else:
            plot(counts[col]["count"],
                title=f"Risk Ads Count by {col.replace('_',' ').title()}",
                out=f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/{col}_label_count.png",
                xlabel="Count")
            
            plot(counts[col]["normalized"],
                title=f"Normalized Risk Ads Distribution by {col.replace('_',' ').title()}",
                out=f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/{col}_label_distribution.png",
                xlabel="Proportion")
   

def overlap(df):
    gender_pref_by_industry = {}
    gender_pref =df["gender preference"].tolist()
    job_type    = df["job type"].tolist()
    our_labels  = df["Our_Model_label"].tolist()

    for i in range(len(df)):
        gp = gender_pref[i]
        jt = job_type[i]
        if jt not in gender_pref_by_industry.keys():
            gender_pref_by_industry[jt] = {"Female": 0, "Male": 0, "No Preference": 0, "Couple": 0}
        gender_pref_by_industry[jt][gp] += 1

    risk_counts = {}
    for i in range(len(our_labels)):
        label = our_labels[i]
        jt = job_type[i]
        gp = gender_pref[i]
        if jt not in risk_counts.keys():
            risk_counts[jt] = {"safe": 0, "risk": 0}
        risk_counts[jt][label] += 1
    
    femele_couple_rates = []
    risk_rate =[]
    industry = []

    for key in gender_pref_by_industry.keys():
        total = sum(gender_pref_by_industry[key].values())
        female_count = gender_pref_by_industry[key].get("Female", 0) + gender_pref_by_industry[key].get("Couple", 0)
        female_rate = female_count / total if total > 0 else 0
        femele_couple_rates.append(female_rate)
        r_total = risk_counts[key]["safe"] + risk_counts[key]["risk"]
        r_rate = risk_counts[key]["risk"] / r_total if r_total > 0 else 0
        risk_rate.append(r_rate)
        industry.append(key)
    
    # Scatter plot for female_couple_rates vs risk_rate
    plt.figure(figsize=(16, 8))
    plt.scatter(femele_couple_rates, risk_rate, color='purple')
    plt.xlabel("Female+Couple Rate by Industry")
    plt.ylabel("Risk Rate by Industry")
    plt.title("Female+Couple Rate vs Risk Rate by Industry")

    # Linear regression fit

    X = np.array(femele_couple_rates).reshape(-1, 1)
    y = np.array(risk_rate)
    reg = LinearRegression().fit(X, y)
    k = 10
    idx_sorted = np.argsort(risk_rate)[::-1]  # descending
    label_idx = set(idx_sorted[:k])

    for i, txt in enumerate(industry):
        if i not in label_idx:
            continue
        x_val = femele_couple_rates[i]
        y_val = risk_rate[i]
        if txt == "Hospitality":
        # Put below the point
            plt.annotate(
                txt,
                (x_val, y_val),
                fontsize=8,
                xytext=(0, -12),     # 12 px DOWN
                textcoords='offset points',
                ha='center',
                va='top'             # anchor above the offset, so text sits below
            )
            continue
        plt.annotate(
            txt,
            (femele_couple_rates[i], risk_rate[i]),
            fontsize=8,
            xytext=(5, 5),
            textcoords='offset points',
            ha='left',
            va='bottom',
            arrowprops=dict(arrowstyle='-', lw=0.5, color='gray', alpha=0.5)
        )

    y_pred = reg.predict(X)
    plt.plot(femele_couple_rates, y_pred, color='orange', label=f"Regression (R²={reg.score(X, y):.2f})")
    plt.legend()
    plt.tight_layout()
    plt.savefig("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/female_couple_vs_risk_scatter.png", dpi=300)
    plt.close()
    


    
    
if __name__ == "__main__":
    dirPath  = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_with_original_labels.csv"
    df = pd.read_csv(dirPath, low_memory=False)
    original_labels = df["original_label"].tolist()
    our_labels = df["Our_Model_label"].tolist()
    valid_pairs = [(o, u) for o, u in zip(original_labels, our_labels) if o != "unknown"]
    get_label_counts(df)
    #eval_our_model(valid_pairs)
    plot_all(df)
    #overlap(df)
    
