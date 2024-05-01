import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from translate import Translator
from dateutil.relativedelta import relativedelta
import matplotlib.dates as mdates



def count_contact(data):
    contact = {"email": 0, "phone":0, "both":0}
    for file in data:
        for d in data[file]:
            if len(data[file][d]["emails"]) > 0 and len(data[file][d]["phone_numbers"]) >0:
                contact["both"] +=1
                contact["email"] += len(data[file][d]["emails"])
                contact["phone"] += len(data[file][d]["phone_numbers"])
            elif len(data[file][d]["emails"]) > 0:
                contact["email"] += len(data[file][d]["emails"])
            elif len(data[file][d]["phone_numbers"]) >0:
                contact["phone"] += len(data[file][d]["phone_numbers"])

    frame = {"Contact": ["Email", "Phone", "Both"], "Number": [contact["email"], contact["phone"],contact["both"]]}
    df = pd.DataFrame.from_dict(frame)
    fn = "count_by_contact.csv"
    df.to_csv(fn, index=False)
    return contact

def sort_by_industry(data):
    industry = {}
    for file in data:
        for d in data[file]:
            print(data[file][d].keys())
            if '行业' not in data[file][d].keys():
                print("行业 not in keys")
                continue
            ind = data[file][d]['行业']
            key = file+"_"+d
            if ind == "餐厅":
                ind = "餐饮"
            if ind not in industry.keys():
                industry[ind] = {}
            industry[ind][key] = data[file][d]

    frame = {"Industry":[], "Number" : []}
    for key in industry.keys():
        frame["Industry"].append(key)
        frame["Number"].append(len(industry[key]))
    df = pd.DataFrame.from_dict(frame)
    fn = "count_by_industry.csv"
    df.to_csv(fn, index=False)
    return industry

def count_contact_by_industry(data):
    ind = {}
    for industry in data:
        contact = {"email": 0, "phone": 0, "both": 0}
        lsts = data[industry]
        for d in lsts:
            if len(lsts[d]["emails"]) > 0 and len(lsts[d]["phone_numbers"]) > 0:
                contact["both"] += 1
                contact["email"] += len(lsts[d]["emails"])
                contact["phone"] += len(lsts[d]["phone_numbers"])
            elif len(lsts[d]["emails"]) > 0:
                contact["email"] += len(lsts[d]["emails"])
            elif len(lsts[d]["phone_numbers"]) > 0:
                contact["phone"] += len(lsts[d]["phone_numbers"])
        ind[industry] = contact

    frame = {"Industry": [], "Email": [], "Phone": [], "Both":[]}
    for i in ind:
        frame["Industry"].append(i)
        frame["Email"].append(ind[i]["email"])
        frame["Phone"].append(ind[i]["phone"])
        frame["Both"].append(ind[i]["both"])
    df = pd.DataFrame.from_dict(frame)
    fn = "count_contact_by_industry.csv"
    df.to_csv(fn, index=False)
    return ind

def convert_date_time(lst):
    new_lst = []
    for dateStr in lst:
        date_object = datetime.strptime(dateStr, '%Y/%m/%d').date()
        year_month = datetime(date_object.year, date_object.month, 1)
        new_lst.append(year_month)
    return new_lst

def generate_time_axis(lst):
    maxi = max(lst)
    mini = datetime.strptime("2019/01/01", '%Y/%m/%d').date()
    start = datetime(mini.year, mini.month, 1)
    end = datetime(maxi.year, maxi.month, 1)
    date_dict = {}
    while start <= end:
        date_dict[start] = 0
        start += relativedelta(months=1)
    return date_dict

def analyze_publish_freq(data):
    occurance = convert_date_time(data)
    freq = generate_time_axis(occurance)
    for d in occurance:
        if d in freq.keys():
            freq[d] += 1
    return freq

"""
def convert_date_time(lst):
    new_lst = []
    for dateStr in lst:
        date_object = datetime.strptime(dateStr, '%Y/%m/%d').date()
        new_lst.append(date_object)
    return new_lst


def generate_time_axis(lst):
    maxi = max(lst)
    mini = datetime.strptime("2019/01/01", '%Y/%m/%d').date()
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


def analyze_publish_freq(data):
    #creation_date = convert_date_time(data["date created"])
    #modify_date = convert_date_time(data["date modified"])
    occurance = convert_date_time(data)
    freq = generate_time_axis(occurance)
    #modify_freq = generate_time_axis(modify_date)
    for d in occurance:
        if d in freq.keys():
            freq[d] += 1
  return freq
"""
def plot_time_series(data, title, outname):
    dates = list(data.keys())
    y = list(data.values())
    plt.figure(figsize=(10, 5))
    plt.plot(dates, y, linewidth=1)

    plt.xlabel("Time (By Month)")
    plt.ylabel("Number of job ads posted")
    plt.title(title)
    plt.gcf().autofmt_xdate()
    plt.savefig(outname, dpi=300)
    plt.close


def analyze_posting_activity(data, fname):
    time_data = []
    for file in data:
        for d in data[file]:
            if "date_created" in data[file][d].keys():
                time_data.append(data[file][d]["date_created"].split(" ")[0])
            if "date_modified" in data[file][d].keys():
                time_data.append(data[file][d]["date_modified"].split(" ")[0])
    all_activities = analyze_publish_freq(time_data)
    plot_time_series(all_activities, "Posting frequencies of all industries", fname)


def analyze_posting_activity_by_industry(data, industry, fname):
    time_data = []
    for d in data:
        if "date_created" in data[d].keys():
            time_data.append(data[d]["date_created"].split(" ")[0])
        if "date_modified" in data[d].keys():
            time_data.append(data[d]["date_modified"].split(" ")[0])
    all_activities = analyze_publish_freq(time_data)
    title = "Posting frequencies of "+industry
    plot_time_series(all_activities, title, fname)
    return all_activities

def main():
    translator_dict = {"其他":"other",
                       "销售":"Sale",
                       "电脑相关":"Computer related",
                       "司机" :"Driver",
                       "餐饮": "Retaurant",
                       "仓库":"Warehouse",
                       "保姆/家政" : "Nanny",
                       "文职人员": "Clerk",
                       "文员": "Service",}
    current = os.getcwd()
    path = current + '/framed_data/'
    print(path)
    all_files = os.listdir(path)
    file_names = [item for item in all_files if os.path.isfile(os.path.join(path, item))]
    print(file_names)
    all_data = {}
    for f in file_names:
        f_path = path+f
        print(f_path)
        data = json.load(open(f_path,"r"))
        all_data[f] = data

    #contacts_proportion = count_contact(all_data)
    by_industry = sort_by_industry(all_data)
    #contact_by_industry = count_contact_by_industry(by_industry)
    analyze_posting_activity(all_data, "freq_all.png")
    activities = {}
    for ind in by_industry:
        fn = "freq_"+translator_dict[ind].split("/")[0]+".png"
        activity = analyze_posting_activity_by_industry(by_industry[ind], translator_dict[ind],fn )
        activities[ind] = activity

    plt.figure(figsize=(10,5))
    for ind in activities:
        dates = list(activities[ind].keys())
        y = list(activities[ind].values())
        plt.plot(dates, y, label=translator_dict[ind], linewidth=1)
    plt.xlabel("Time (By Month)")
    plt.ylabel("Number of job ads posted")
    plt.legend(fontsize="5")
    plt.title("Posting Frequency By Industry")
    plt.gcf().autofmt_xdate()
    plt.savefig("Frequency by industry", dpi=300)





if __name__ == "__main__":
    main()