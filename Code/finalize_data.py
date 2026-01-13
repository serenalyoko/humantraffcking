import pandas as pd
import json
import os
import re


def preprocess_text(text):
    text = text.strip().lower()
    text = text.replace("<p>", "")
    text = text.replace("</p>", "")
    text = re.sub('<[^<]+?>', '', text)
    return text
def contains_html(text):
    html_pattern = re.compile(r'<[^>]+>')
    tags = re.findall(r"<[^>]+>", text)
    return bool(html_pattern.search(text)), tags

def contains_java(text):
    java_pattern = re.compile(r'javascript:[^\'"]*')
    tags = re.findall(r'javascript:[^\'"]*', text)
    return bool(java_pattern.search(text)), tags
def contains_css(text):
    css_pattern = re.compile(r'style=[\'"][^\'"]*[\'"]')
    tags = re.findall(r'style=[\'"][^\'"]*[\'"]', text)
    return bool(css_pattern.search(text)), tags
    
if __name__ == "__main__":

    path1 = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd.csv"
    path2 = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/unified_data.csv"
    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    df1 = df1.fillna("")
    df2 = df2.fillna("")
    titles2 = df2['title'].tolist()
    desc2 = df2['description'].tolist()
    locations2 = df2['location'].tolist()
    timestamps2 = df2['date'].tolist()
    repeats2 = df2['repeat'].tolist()
    labels2 = df2['label'].tolist()
   
    all_data = {"description":[], "date":[], "location":[], "repeat": [], "domains":[], "label":[]}
    description_index = {}
    risk = 0
    safe = 0
    risk_empty = 0
    safe_empty = 0
    html_count = {"safe":0, "risk":0}
    java_count = {"safe":0, "risk":0}
    css_count = {"safe":0, "risk":0}
    for i in range(len(titles2)):
        desc = titles2[i]+desc2[i]
        desc = preprocess_text(desc)
        hasHTML, htmltags = contains_html(desc)
        hasJava, javatags = contains_java(desc)
        hasCSS, csstags = contains_css(desc)
        if hasHTML:
            html_count[labels2[i]] += 1
            print(htmltags)
            
        if contains_java(desc):
            java_count[labels2[i]] += 1
            print(javatags)
            
        if contains_css(desc):
            css_count[labels2[i]] += 1
            print(csstags)
            
        for t in htmltags:
            desc = desc.replace(t, " ")
        for t in javatags:
            desc = desc.replace(t, " ")
        for t in csstags:
            desc = desc.replace(t, " ")
        
        all_data["description"].append(desc )
        all_data["date"].append(timestamps2[i])
        all_data["location"].append(locations2[i])
        all_data["repeat"].append(repeats2[i])
        all_data["domains"].append(["unified_data"])
        all_data["label"].append(preprocess_text(labels2[i]))
        description_index[desc] = i
        if labels2[i] == "risk":
            risk += 1
            if desc == "":
                risk_empty += 1
        else:
            safe += 1
            if desc == "":
                safe_empty += 1
    
    start = len(titles2) # len = 3, [0, 1,2]
    desc = df1['job description'].tolist()
    locations = df1['location'].tolist()
    timestamps = df1['timestamp'].tolist()
    labels = df1['label'].tolist()
    file_ids = df1['file id'].tolist()
    job_ids = df1['job id'].tolist()
    print(len(all_data["description"]), len(description_index.keys()))
    for j in range(len(desc)):
        descr = preprocess_text(desc[j])
        hasHTML, tags = contains_html(descr)
        hasHTML, htmltags = contains_html(descr)
        hasJava, javatags = contains_java(descr)
        hasCSS, csstags = contains_css(descr)
        if hasHTML:
            html_count[labels[j]] += 1
            print(htmltags)
            
        if contains_java(descr):
            java_count[labels[j]] += 1
            print(javatags)
            
        if contains_css(descr):
            css_count[labels[j]] += 1
            print(csstags)
            
        for t in htmltags:
            descr = descr.replace(t, " ")
        for t in javatags:
            descr = descr.replace(t, " ")
        for t in csstags:
            descr = descr.replace(t, " ")
        
        if descr in description_index.keys():
            idx = description_index[descr]
            #print(idx, len(all_data["repeat"]))
            all_data["repeat"][idx] += 1
            all_data["domains"][idx].append(file_ids[j].split(".")[0] + str(job_ids[j]))
        else:
            new_idx = len(all_data["description"])
            #print(f"new index = {new_idx}")
            description_index[descr] = new_idx
            all_data["description"].append(descr)
            all_data["date"].append(timestamps[j])
            all_data["location"].append(locations[j])
            all_data["repeat"].append(0)
            all_data["domains"].append([file_ids[j].split(".")[0] + str(job_ids[j])])
            all_data["label"].append(labels[j])
            if labels[j] == "risk":
                risk += 1
                if desc[j] == "":
                    risk_empty += 1
            else:
                safe += 1
                if desc[j] == "":
                    safe_empty += 1
    print("Total risk:", risk)
    print("Total safe:", safe)
    print("Total risk empty:", risk_empty)
    print("Total safe empty:", safe_empty)
    
    for key, value in html_count.items():
        print(f"Total {key} with HTML:", value)
    for key, value in java_count.items():
        print(f"Total {key} with JavaScript:", value)
    for key, value in css_count.items():
        print(f"Total {key} with CSS:", value)

    df = pd.DataFrame(all_data)
    df.to_csv("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/finalized_data.csv", index=False, encoding='utf-8-sig')