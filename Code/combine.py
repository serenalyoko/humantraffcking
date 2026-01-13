import os
import json
import pandas as pd

def retrieve_rusrek(access_file, access_id):
    try:
        with open(access_file, 'r') as f:
            data = json.load(f)
        job = data[access_id]
        if "by_page" in access_file:
            job_descrip = job["title"] + " " + job['description']
            location = "N/A"
            timestamp = "N/A"
        else:
            job_descrip = job["title"] + " " + job['description_text']
            location = job['location']
            timestamp = job["date_updated"]
        return job_descrip, location, timestamp
    except (KeyError, FileNotFoundError, json.JSONDecodeError):
        return "", "", ""

def retrieve_500work(access_file, access_id):
    try:
        with open(access_file, 'r') as f:
            data = json.load(f)
        job = data[access_id]
        job_descrip = job["title"] + " " + job['description']
        location = job['location']
        job_timestamp = job['date']
        return job_descrip, location, job_timestamp
    except (KeyError, FileNotFoundError, json.JSONDecodeError):
        return "", "", ""

def retrieve_chinesein(access_file, access_id):
    try:
        with open(access_file, 'r') as f:
            data = json.load(f)
        job = data[access_id]
        job_descrip = job["title"] + " " + job['job_descripton']
        location = job.get('地点') or job.get('地址')
        timestamp = job['date_created']
        return job_descrip, location, timestamp
    except (KeyError, FileNotFoundError, json.JSONDecodeError):
        return "", "", ""

def retrieve(access_file, access_id):
    if access_file is None or access_file == "None":
        return "", "", ""
    if "chin" in access_file:
        return retrieve_chinesein(access_file, access_id)
    elif "rusrek" in access_file:
        return retrieve_rusrek(access_file, access_id)
    elif "500work" in access_file:
        return retrieve_500work(access_file, access_id)
    return "", "", ""

def get_label(labels):
    if ("job_board" in labels or "social_media" in labels) and ("escort" in labels):
        return "risk"
    else:
        return "safe"
def get_filepath(access_file, jobAdsPaths):
    for path in jobAdsPaths:
        if access_file in path:
            return path
    return None


if __name__ == "__main__":
    rusrekPath = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/Rusrek_by_page/" 
    rusrek_files = os.listdir(rusrekPath)
    metaPath =  "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/phone_num_network_meta_0825_cleaned_finalized.json"
    jobAdsPaths = ["/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/escort_data.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/rusrek_data.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/500work.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/chineseinatlanta_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/chineseinflorida_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/chineseinla_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/chineseinsfbay_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/dcchinaren_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/nychinaren_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/seattlechinaren_url.json",
                      "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/extracted_data/vegaschinaren_url.json"]
    for file in rusrek_files:
        if file.endswith(".json"):
            jobAdsPaths.append(os.path.join(rusrekPath, file))
    outputPath = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd.json"

    # Load metadata
    with open(metaPath, 'r') as f:
        metadata = json.load(f)

    labeled_data = {"file id":[], "job id":[], "job description":[], "location":[], "timestamp":[], "label":[]}

    risk = 0
    for phone_number in metadata.keys():
        #print(metadata[phone_number].keys())
        access_files = metadata[phone_number]['access_file']
        access_ids = metadata[phone_number]['access_key']
        #print(phone_number, access_files, access_ids)
        labels = metadata[phone_number]['label']
        label = get_label(labels)
        #print(label)
        for i in range(len(access_files)):
            if "500work" in access_files[i]:
                access_files[i] = '500work.json'
            filePath = get_filepath(access_files[i], jobAdsPaths)
            print(access_files[i], filePath, access_ids[i])

            access_key = access_ids[i]
            file_id = access_files[i]
            job_descrip, location, timestamp = retrieve(filePath, access_key)

            labeled_data["file id"].append(file_id)
            labeled_data["job id"].append(access_key)
            labeled_data["job description"].append(job_descrip)
            labeled_data["location"].append(location)
            labeled_data["timestamp"].append(timestamp)
            labeled_data["label"].append(label)
            if label == "risk":
                risk += 1
    print("Total risk:", risk)
    df = pd.DataFrame(labeled_data)
    df.to_json(outputPath, orient='records', lines=True)
            
