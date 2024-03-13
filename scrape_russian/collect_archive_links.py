import subprocess
import pandas as pd
import pickle
import os

def retreive_archive(url):
    curl_command = " curl -X GET http://web.archive.org/cdx/search/cdx?url=" + url
    # Execute the curl command
    process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # Get the output and error (if any)
    output, error = process.communicate()
    # Decode the output to a string
    response = output.decode('utf-8')

    # Convert the response to a pandas DataFrame
    # This assumes that the response is in JSON format
    seg = url.split("/")
    fname = "newyork.p"
    if len(seg) > 6:
        fname = seg[5] + ".p"
    # Save the DataFrame to a CSV file
    pickle.dump(response, open(fname, "w"))


def parse_res_data(res_file):
    f = open(res_file)
    lines = f.readlines()
    data = {"urlkey":[], "timestamp":[], "original":[], "mimetype": [], "statuscode":[], "digest":[], "length":[]}
    for line in lines:
        seg = line.split(" ")
        data["urlkey"].append(seg[0])
        data["timestamp"].append(seg[1])
        data["original"].append(seg[2])
        data["mimetype"].append(seg[3])
        data["statuscode"].append(seg[4])
        data["digest"].append(seg[5])
        data["length"].append(seg[6])
    return data



if __name__ == "__main__":
    links = [
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/",
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/los-angeles/",
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/san-francisco/",
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/washington/",
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/miami/",
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/seattle/",
        "https://rusrek.com/mall/job_help_wanted-b381934_0-ru/atlanta/"
    ]

    # Define your curl command
    for url in links:
        retreive_archive(url)
    path = "/Users/siyizhou/Documents/ISI/humanTrafficking/pythonProject/scrape_russian/archive_links"
    files = os.listdir(path)
    archive_data = {"urlkey":[], "timestamp":[], "original":[], "mimetype": [], "statuscode":[], "digest":[], "length":[]}

    for f in files:
        data = parse_res_data(f)
        archive_data["urlkey"] += data["urlkey"]
        archive_data["timestamp"] += data["timestamp"]
        archive_data["original"] += data["original"]
        archive_data["mimetype"] += data["mimetype"]
        archive_data["statuscode"] += data["statuscode"]
        archive_data["digest"] += data["digest"]
        archive_data["length"] += data["lenth"]




