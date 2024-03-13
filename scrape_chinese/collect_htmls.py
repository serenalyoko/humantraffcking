import utility
import pandas as pd
import os

def main():
    directory_path = '/Users/siyizhou/Documents/ISI/humanTrafficking/pythonProject/scrape_chinese/all_links'
    all_files = os.listdir(directory_path)
    file_names = [item for item in all_files if os.path.isfile(os.path.join(directory_path, item))]

    for n in file_names:
        dir_name = n.split(".")[0]
        df = pd.read_csv(n)
        url = df["url"]
        utility.save_job_post_html(url, dir_name)


if __name__ == "__main__":
    main()