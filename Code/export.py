import json
import pandas as pd
import os

if __name__ == "__main__":
    path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd.json"
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    
    
    reformat_data = {}
    labeled_data = {"file id":[], "job id":[], "job description":[], "location":[], "timestamp":[], "label":[]}
    
    for item in data:
        file_id = item.get("file id", "N/A")
        job_id = item.get("job id", "N/A")
        if "escort" in file_id.lower():
            continue
        if file_id not in reformat_data.keys():
            reformat_data[file_id] = {}
        
        if job_id not in reformat_data[file_id].keys():
            reformat_data[file_id][job_id] = {}
        
        job_description = item.get("job description", "N/A")
        location = item.get("location", "N/A")
        timestamp = item.get("timestamp", "N/A")
        label = item.get("label", "N/A")
        reformat_data[file_id][job_id] = {
            "job description": job_description,
            "location": location,
            "timestamp": timestamp,
            "label": label
        }

    stats = {"safe":0, "risk":0, "safe_empty":0, "risk_empty":0, "safe_escort" :0, "risk_escort":0}
    for file_id in reformat_data.keys():
        for job_id in reformat_data[file_id].keys():
            job_description = reformat_data[file_id][job_id]["job description"]
            location = reformat_data[file_id][job_id]["location"]
            timestamp = reformat_data[file_id][job_id]["timestamp"]
            label = reformat_data[file_id][job_id]["label"]

            labeled_data["file id"].append(file_id)
            labeled_data["job id"].append(job_id)
            labeled_data["job description"].append(job_description)
            labeled_data["location"].append(location)
            labeled_data["timestamp"].append(timestamp)
            labeled_data["label"].append(label)
            if label == "safe":
                stats["safe"] += 1
                if job_description.strip() == "":
                    stats["safe_empty"] += 1
            elif label == "risk":
                stats["risk"] += 1
                if job_description.strip() == "":
                    stats["risk_empty"] += 1
    

    stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['count'])
    stats_df.to_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/stats.csv", encoding='utf-8-sig')
    df = pd.DataFrame(labeled_data)
    df.to_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd.csv", index=False, encoding='utf-8-sig')