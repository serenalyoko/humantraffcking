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
https://newyork.craigslist.org/
https://losangeles.craigslist.org/search/jjj#search=1~thumb~0~0
https://seattle.craigslist.org/
https://sfbay.craigslist.org/
https://lasvegas.craigslist.org/
https://miami.craigslist.org/
https://atlanta.craigslist.org/
https://washingtondc.craigslist.org/

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


def scrape_job_post(url):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
    except:
        return
    sleep(1)
    page_source = driver.page_source

    fname = url.split("/")[4] + ".html"
    n = os.path.join("/Users/siyizhou/Documents/ISI/humanTrafficking/rusrek_data/20230207", fname)
    # open file in write mode with encoding
    f = codecs.open(n, "w+", "utf−8")
    f.write(page_source)

    soup = BeautifulSoup(page_source, 'html.parser')
    #headline = soup.select("span[*='Healine']")
    selector = ["div.der-title", "a.banner-phone", "a.banner-email", "div.tab_container", "ul.bottm-list>li"]
    info = {"url": url}
    for s in selector:
        type = s.split(".")
        data = soup.select(s)
        for d in data:
            if type[0] == "a":
                info[type[1]] = d['href']
            if type[0] == "div":
                info[type[1]] = d.text
            if type[0] == "ul":
                key = d['title']
                val = d.text
                info[key] = val

    return info

def scrape_all_job_posts(infile, outfile):
    df =pd.read_csv(infile)
    urls = df["url"]
    all_posts = {"url":[], "title":[], "email": [], "phone": [], "post": [], "date created": [], "date modified": [], "views":[]}
    for url in urls:
        data = scrape_job_post(url)
        all_posts["url"].append(url)
        all_posts["title"].append(data["der-title"])
        try:
            all_posts["email"].append(data["banner-email"])
        except KeyError:
            all_posts["email"].append("")
        try:
            all_posts["phone"].append(data["banner-phone"])
        except KeyError:
            all_posts["phone"].append("")
        all_posts["post"].append(data["tab_container"])
        #all_posts["date created"].append(data["Дата добавления"])
        all_posts["date modified"].append(data["Дата обновления"])
        #all_posts["views"].append(data["Интересовались"])
    f = open(outfile, "wb")
    obj = json.dumps(all_posts, indent=4, ensure_ascii=False).encode('utf8')
    f.write(obj)

if __name__ == "__main__":
    scrape_links("https://losangeles.craigslist.org/search/jjj#search=1", 50, "all_job_postings_links.csv")
    #print(scrape_job_post("https://rusrek.com/mall/priglashaem_zhenshchin_8091508"))
    #scrape_all_job_posts("massage_parlor_links.csv", "massage_parlor_posts.json")

    #scrape_all_job_posts("all_job_postings_links.csv", "all_job_postings_posts.json")