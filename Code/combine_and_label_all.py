import json
import os

import pandas as pd


def get_field(keywords, data):
    field = ""
    #print(data.keys())
    for key in keywords:
        if key in data.keys():
            if "contact" in keywords:
                print(data[key])
            if isinstance(data[key], dict):
                for key2 in keywords:
                    if key2 in data[key].keys():
                        field += str(data[key][key2]) + " "
            else:
                field += str(data[key]) + " "
    return field.strip()

def get_domain_location(domain):
    locations = ["chicago", "atlanta", "florida", "houston", "la", "ny", "pa", "sf", "dc", "seattle", "vegas"]
    for loc in locations:
        if loc in domain.lower():
            return loc
    return "unknown"


def main():
    dirPath  = "/Users/d22admin/Documents/human-trafficking/data_cleaning/ExtractedData"
    files = os.listdir(dirPath)
    all_data = {"job ID":[],"job_description": [], "domain":[], "domain location":[], "job type":[], "location": [], "contact method":[], "full/part time": [], "salary": []}
    keywords = {
        "job_description": [ "title","job_description", "description", "job_descripton", "description", "description_text"],
        "job type": ["job type", "行业", "category"],
        "location": ["location", "address", "地址", "地点", "jobLocation", "contact_details", "region"],
        "contact method": ["contact_phone", "contact", "phone", "emails", "phone_numbers", "contact_details", "phones"],
        "salary": ["salary", "pay", "compensation"],
        "full/part time": ["工作性质"]
    }


    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(dirPath, file)
            with open(file_path, "r") as f:
                data = json.load(f)
            domain = file.replace(".json", "").replace("_url", "")
            domain_location = get_domain_location(domain)
            for job in data.keys():
                all_data["job ID"].append(job)
                all_data["job_description"].append(get_field(keywords["job_description"], data[job]))
                all_data["job type"].append(get_field(keywords["job type"], data[job]))
                all_data["location"].append(get_field(keywords["location"], data[job]))
                all_data["contact method"].append(get_field(keywords["contact method"], data[job]))
                all_data["salary"].append(get_field(keywords["salary"], data[job]))
                all_data["full/part time"].append(get_field(keywords["full/part time"], data[job]))
                all_data["domain"].append(domain)
                all_data["domain location"].append(domain_location)
    df = pd.DataFrame(all_data)
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()