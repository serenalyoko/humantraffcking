import pandas as pd

def unify_file_id(text):
    domain = text.lower().replace("_url.json", "").replace("_data.json", "").replace(".json", "")
    return domain
def find_duplicate_pairs(id_list, domain_list):
    counts = {}
    for job_id, domain in zip(id_list, domain_list):
        pair = (job_id, domain)
        if pair in counts:
            counts[pair] += 1
            print(f"Duplicate found: {pair}")
        else:
            counts[pair] = 1
    return counts

def find_mapped_posts(original_pairs, current_pairs):
    mapped = []
    count = 0
    for orig_id, orig_domain in original_pairs:
        if (orig_id, orig_domain) in current_pairs:
            mapped.append((orig_id, orig_domain))
            count += 1
    print(f"Total mapped posts: {count}")
    return mapped


if __name__ == "__main__":
    original_labels_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/labeled_jd.csv"
    current_dataset = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_4.0.csv"
    additional_cols = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_3.0.csv"
    df_original = pd.read_csv(original_labels_path, low_memory=False)
    df_current  = pd.read_csv(current_dataset, low_memory=False)
    df_additional = pd.read_csv(additional_cols, low_memory=False)

    df_original["file id"] = df_original["file id"].apply(unify_file_id)
    original_label = df_original["label"].tolist()
    original_domains = df_original["file id"].tolist()
    print(set(original_domains))
    print()
    original_jobids= df_original["job id"].tolist()
    jobids_current = df_current["job ID"].tolist()
    domain_current  = df_current["domain"]
    phone_numbers_additional = df_additional["extracted phone numbers"].tolist()
    gender_preferences = df_additional["gender preference"].tolist()
    job_locations_additional = df_additional["location"].tolist()
    df_current["extracted phone numbers"] = phone_numbers_additional
    df_current["gender preference"] = gender_preferences
    df_current["location"] = job_locations_additional

    #print("Finding non-unique job IDs in original labels:")
    #original_counts = find_duplicate_pairs(jobids_original, df_original["file id"].tolist())
    #print("Finding non-unique job IDs in current dataset:")
    #current_counts = find_duplicate_pairs(jobids_current, df_current["domain"].tolist())
    
    original_labels = {}
    for i in range(len(original_label)):
        pair = (original_domains[i], original_jobids[i])
        original_labels[pair] = original_label[i]

    
    
    mapped = 0
    original_label = ["unknown" for _ in range(len(df_current))]

    for i in range(len(df_current)):
        job_id = jobids_current[i]
    
        domain = domain_current[i]
        if (domain, job_id) in original_labels.keys():
            original_label[i] = original_labels[(domain, job_id)]
            mapped += 1
    print(f"Total mapped posts with original labels: {mapped} out of {len(df_current)}")
    df_current["original_label"] = original_label
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_with_original_labels.csv"
    df_current.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved combined dataset with original labels to: {output_path}")

