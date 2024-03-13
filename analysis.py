import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def convert_date_time(lst):
    new_lst = []
    for dateStr in lst:
        date_object = datetime.strptime(dateStr, '%m/%d/%Y').date()
        new_lst.append(date_object)
    return new_lst


def generate_time_axis(lst):
    maxi = max(lst)
    mini = min(lst)
    #print(maxi)
    #print(mini)
    start = mini
    end = maxi
    date_dict = {}
    while start <= end:
        date_dict[start] = 0
        #print(start.strftime('%m/%d/%Y'))
        start += timedelta(days=1)
    return date_dict


def analyze_publish_freq(fname):
    data = json.load(open(fname))
    creation_date = convert_date_time(data["date created"])
    modify_date = convert_date_time(data["date modified"])
    creation_freq = generate_time_axis(creation_date)
    modify_freq = generate_time_axis(modify_date)
    for d in creation_date:
        creation_freq[d] += 1
    for d in modify_date:
        modify_freq[d] += 1
    return creation_freq, modify_freq

def plot_time_series(data, title, outname):
    dates = list(data.keys())
    y = list(data.values())
    fig, ax = plt.subplots()
    ax.plot(dates, y, linewidth=2.0)
    plt.title(title)
    plt.gcf().autofmt_xdate()
    plt.savefig(outname, dpi=300)


if __name__ == "__main__":
    massage_creation_freq, massage_modify_freq = analyze_publish_freq("massage_parlor_posts.json")
    all_job_creation_freq, all_job_modify_freq = analyze_publish_freq("all_job_postings_posts.json")
    plot_time_series(massage_modify_freq, "Massage Parlor listing frequency by modification date", "massage_mod_freq.png")
    plot_time_series(massage_creation_freq, "Massage Parlor listing frequency by creation date", "massage_create_freq.png")
    plot_time_series(all_job_modify_freq, "All job listing frequency by modification date", "all_job_mod_freq.png")
    plot_time_series(all_job_creation_freq, "All job listing frequency by creation date", "all_job_create_freq.png")
