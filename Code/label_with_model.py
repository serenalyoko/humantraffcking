import pandas as pd


if __name__ == "__main__":
    path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_3.0.csv"
    df = pd.read_csv(path, low_memory=False)
    df = df[["job ID", "job_description", "domain"]]
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_embedding.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")