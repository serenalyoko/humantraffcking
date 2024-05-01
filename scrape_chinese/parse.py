import utility
import pandas as pd
from bs4 import BeautifulSoup
import os
import json

def main():
    current = os.getcwd()
    directory_path = current + '/htmls/'
    print(directory_path)
    all_files = os.listdir(directory_path)
    dir_names = [item for item in all_files if os.path.isdir(os.path.join(directory_path, item))]
    print(dir_names)
    for d in dir_names:
        print(d)
        if d == ".DS_Stored":
            continue
        dir_name = current + "/htmls/" + d + "/"
        files = os.listdir(dir_name)
        file_names = [file for file in files if os.path.isfile(os.path.join(dir_name, file))]
        print(dir_name)
        print(file_names)
        all_data = {}
        for n in file_names:
            print(n)
            if ".html" not in n:
                continue
            print(n)
            # Read the contents of the HTML file
            file_path = dir_name + n

            with open(file_path, 'r') as f:
                html_code = f.read()

            # Parse the HTML using Beautiful Soup
            soup = BeautifulSoup(html_code, 'html.parser')
            data = utility.collect_data_point(soup)
            all_data[n] = data
        fname = d + ".json"
        f = open(fname, "wb")
        obj = json.dumps(all_data, indent=4, ensure_ascii=False).encode('utf8')
        f.write(obj)
        f.close()



if __name__ == "__main__":
    main()