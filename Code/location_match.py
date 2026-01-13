import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

"""
Have three locations are valid
phone mismatch: phone is different from domain location and job location
domain mismatch: domain location is different from phone location and job location
job mismatch: job location is different from domain location and phone location
all mismatch: all three locations are different

Have 1 location unknown:
phone unknown: match domain and job, mismatch
location unknown: match phone and domain, mismatch
domain unknown: match phone and job, mismatch

More than two unknown location: not comparable
"""

def match_location(domain_loc, phone_loc, job_loc):
    if domain_loc == "unknown":
        if phone_loc.lower() == "unknown" or job_loc.lower() == "not specified":
            return "Not comparable"
        if phone_loc.lower() != job_loc.lower():
            return "domain location unspecified, mismatch"
        else:
            return "domain location unspecified, match"
    if phone_loc.lower() == "unknown" :
        if domain_loc.lower() == "unknown" or job_loc.lower() == "not specified":
            return "Not comparable"
        if domain_loc.lower() != job_loc.lower():
            return "phone location unknown, mismatch"
        else:
            return "phone location unknown, match"
    if job_loc.lower() == "not specified":
        if domain_loc.lower() == "unknown" or phone_loc.lower() == "unknown":
            return "Not comparable"
        if domain_loc.lower() != phone_loc.lower():
            return "job location unknown, mismatch"
        else:
            return "job location unknown, match"
    if phone_loc != domain_loc and domain_loc == job_loc:
        return "phone location mismatch"
    if domain_loc != phone_loc and phone_loc == job_loc:
        return "domain location mismatch"
    if job_loc != domain_loc and domain_loc == phone_loc:
        return "job location mismatch"
    if phone_loc != domain_loc and phone_loc != job_loc and domain_loc != job_loc:
        return "all mismatch"
    return "all match"

def stat(label, job_loc, domain_loc, phone_loc):
    res = {"safe":{
        "all match":0, "all mismatch":0,"phone location mismatch":0, "domain location mismatch":0, "job location mismatch":0,
        "domain location unspecified, match":0, "domain location unspecified, mismatch":0,
        "phone location unknown, match":0, "phone location unknown, mismatch":0,
        "job location unknown, match":0, "job location unknown, mismatch":0,
        "Not comparable":0
        }, 
        "risk":{ "all match":0, "all mismatch":0,"phone location mismatch":0, "domain location mismatch":0, "job location mismatch":0,
        "domain location unspecified, match":0, "domain location unspecified, mismatch":0,
        "phone location unknown, match":0, "phone location unknown, mismatch":0,
        "job location unknown, match":0, "job location unknown, mismatch":0,
        "Not comparable":0}
        }
    safe_total = label.count("safe")
    risk_total = label.count("risk")
    for i in range(len(label)):
        l = label[i]
        jl = job_loc[i]
        dl = domain_loc[i]
        pl = phone_loc[i]
        category = match_location(dl, pl, jl)
        res[l][category] += 1
    
    normnalized = {"safe":{}, "risk":{}}
    for key in res["safe"].keys():
        normnalized["safe"][key] = res["safe"][key] / safe_total
    for key in res["risk"].keys():
        normnalized["risk"][key] = res["risk"][key] / risk_total

    finalized_table = {"type":["safe", "risk"]}
    for key in res["safe"].keys():
        finalized_table[key] = [
            f"{res['safe'][key]}, {normnalized['safe'][key]:.3f}",
            f"{res['risk'][key]}, {normnalized['risk'][key]:.3f}"
        ]
    df = pd.DataFrame(finalized_table)
    df.to_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/location_match_stats.csv", index=False)
    return res, normnalized

def plot(res,decimal, fn):

    categories = list(res["safe"].keys())
    safe_counts = [res["safe"][cat] for cat in categories]
    risk_counts = [res["risk"][cat] for cat in categories]

    bar_width = 0.5
    x = np.arange(2)  # 0 for 'safe', 1 for 'risk'

    # Prepare data for stacking
    safe_stack = np.array(safe_counts)
    risk_stack = np.array(risk_counts)

    bottom_safe = np.zeros(1)
    bottom_risk = np.zeros(1)

    fig, ax = plt.subplots(figsize=(11, 11))
    # Generate a distinct color for each category using tab20 colormap
    # Manually set colors using hex codes
    """"
    all match":0, "all mismatch":0,"phone location mismatch":0, "domain location mismatch":0, "job location mismatch":0,
        "domain location unknown, match":0, "domain location unknown, mismatch":0,
        "phone location unknown, match":0, "phone location unknown, mismatch":0,
        "job location unknown, match":0, "job location unknown, mismatch":0,
        "Not comparable":0
        """
    colors = [
        "#008807","#ff006f","#0011ff", "#f87c00", "#6b0398", "#ffc800",
        "#ffdb81", "#8baaf8", "#306afc", "#9b48bb", "#cea4f6",
        "#A3A3A3", "#848484", "#98df8a", "#ff9896", "#c5b0d5",
        "#c49c94",  "#c7c7c7", "#dbdb8d", "#9edae5"
    ][:len(categories)]
    bars = []
    for i, cat in enumerate(categories):
        bar_safe = ax.bar(x[0], safe_counts[i], bar_width, bottom=bottom_safe, color=colors[i])
        bar_risk = ax.bar(x[1], risk_counts[i], bar_width, bottom=bottom_risk, color=colors[i])
        bars.append(bar_safe[0])  # Save the bar handle for legend
        """
        # Annotate safe bar
        if safe_counts[i] > 0:
            ax.annotate(f'{safe_counts[i]:.2f}',
                        xy=(x[0], bottom_safe + safe_counts[i] / 2),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center', color='black', fontsize=8)

        # Annotate risk bar
        if risk_counts[i] > 0:
            ax.annotate(f'{risk_counts[i]:.2f}',
                        xy=(x[1], bottom_risk + risk_counts[i] / 2),
                        xytext=(5, 8),
                        textcoords="offset points",
                        ha='center', va='center', color='black', fontsize=8)
     """
        bottom_safe += safe_counts[i]
        bottom_risk += risk_counts[i]

    ax.set_xticks(x)
    ax.set_xticklabels(['Safe', 'Risk'])
    ax.set_ylabel('Counts')
    ax.set_title('Stacked Bar Plot of Location Match Categories')
    ax.legend(bars, categories, loc='upper right')
    plt.tight_layout()
    plt.savefig(f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/f{fn}1.png")

  
    categories = list(res["safe"].keys())
    safe_counts = [res["safe"][cat] for cat in categories]
    risk_counts = [res["risk"][cat] for cat in categories]
    x = np.arange(len(categories))
    width = 0.5

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_safe = ax.bar(x, safe_counts, width, label='Safe', color='skyblue')
    bars_risk = ax.bar(x, risk_counts, width, bottom=safe_counts, label='Risk', color='salmon')

    ax.set_xlabel('Location Match Categories')
    ax.set_ylabel('Counts')
    ax.set_title('Location Match Statistics by Label (Stacked)')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()

    for bar in bars_safe:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{height:{decimal}}',
                        xy=(bar.get_x() + bar.get_width() / 2, height / 2),
                        xytext=(0, 2),
                        textcoords="offset points",
                        ha='center', va='center', color='black', fontsize=8)

    for i, bar in enumerate(bars_risk):
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{height:{decimal}}',
                        xy=(bar.get_x() + bar.get_width() / 2, safe_counts[i] + height / 2),
                        xytext=(0, 8),  # Move text 8 points above the bar center
                        textcoords="offset points",
                        ha='center', va='center', color='black', fontsize=8)

    plt.tight_layout()
    plt.savefig(f"/Users/d22admin/Documents/human-trafficking/ContentAnalysis/plots/f{fn}2.png")


if __name__ == "__main__":
    input_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_5.0.csv"
    df = pd.read_csv(input_path, low_memory=False)
    our_labels = df["Our_Model_label"].tolist()
    job_location= df["location"].tolist()
    domain_location = df["domain location"].tolist()
    phone_location = df["phone location"].tolist()
    stats, normalized = stat(our_labels, job_location, domain_location, phone_location)
    plot(stats, ".1f", "location_match_stats")
    plot(normalized, ".3f", "location_match_normalized")