import json
import xlsxwriter
import pandas as pd
import pickle
import numpy as np
from bs4 import BeautifulSoup
import requests
import difflib
from selenium import webdriver
from time import sleep
import codecs
import os


"""
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/los-angeles/
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/san-francisco/
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/washington/
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/miami/
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/seattle/
https://rusrek.com/mall/job_help_wanted-b381934_0-ru/atlanta/

"""


def scrape_link(url, selector):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
    except:
        return
    sleep(2)
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    #headline = soup.select("span[*='Healine']")
    data = soup.select(selector)
    print(data)

    content = []
    for d in data:
        for a in d.find_all('a', href=True):
            content.append(a['href'])
    return content

def scrape_links(url, pagen, fname):
    links = []
    for i in range(0,pagen):
        num = str(i+1)
        link = url + num
        res = scrape_link(link, "h2.ads-header")
        links = links + res
    f = open(fname, "w")
    for l in links:
        li = "https://rusrek.com" +l + "\n"
        f.write(li)
    f.close()

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
    scrape_links("https://rusrek.com/mall/job_help_wanted-b381934_0-ru/?PAGEN_1=", 24, "all_job_postings_links.csv")