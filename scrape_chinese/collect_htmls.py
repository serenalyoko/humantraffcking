import utility
import pandas as pd
import os


def main():
    current = os.getcwd()
    directory_path =  current + '/scrape_chinese/all_links/'
    f = open("log.txt", "a")
    f.write("current_path: ")
    f.write(directory_path)
    f.write("\n")
    print(directory_path)
    all_files = os.listdir(directory_path)
    file_names = [item for item in all_files if os.path.isfile(os.path.join(directory_path, item))]
    for n in file_names:
        print(n)
        dir_name = current+ "/htmls/" + n.split(".")[0]
        df = pd.read_csv(directory_path+n)
        urls = df["url"]
        for url in urls:
            utility.save_job_post_html(url, dir_name)
            line = url + "," + dir_name + "\n"
            f.write(line)
    f.close()


if __name__ == "__main__":
    main()