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
https://www.chineseinla.com/f/page_viewforum/f_29/start_1.html
https://www.chineseinsfbay.com/f/page_viewforum/f_29/start_1.html
https://www.nychinaren.com/f/page_viewforum/f_29/start_1.html
https://www.seattlechinaren.com/f/page_viewforum/f_29/start_1.html
https://www.chineseinatlanta.com/f/page_viewforum/f_29/start_1.html
https://www.chineseinflorida.com/f/page_viewforum/f_29/start_1.html
https://www.vegaschinaren.com/f/page_viewforum/f_29/start_1.html
https://www.dcchinaren.com/f/page_viewforum/f_29/start_1.html

https://500work.com/
https://california.jinbay.com/jobs/
https://www.usahuarenjie.com/category-catid-4-page-1.html

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
    all_items = soup.select("div.topic_list_detail")
    print(len(all_items))
    end = False
    if len(all_items) < 3:
        end = True

    content = []
    for d in data:
        for a in d.find_all('a', href=True):
            content.append(a['href'])
    print(len(content))
    return content, end


def scrape_links(url, pagen, fname):
    links = []
    i = 0
    end = False
    while end is False:
        num = str(i)
        link = url + num+ ".html"
        res = scrape_link(link, "div.havenopage")
        end = res[1]
        if end is True:
            break
        links = links + res[0]
        i = i+15
    f = open(fname, "w")
    for l in links:
        li = l + "\n"
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

    fname = url.split("/")[5]
    n = os.path.join("/Users/siyizhou/Documents/ISI/humanTrafficking/data/20230214/chinese_formal", fname)
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
    domains = ["https://www.vegaschinaren.com/f/page_viewforum/f_29/start_",
             "https://www.chineseinla.com/f/page_viewforum/f_29/start_",
             "https://www.chineseinsfbay.com/f/page_viewforum/f_29/start_",
             "https://www.nychinaren.com/f/page_viewforum/f_29/start_",
             "https://www.seattlechinaren.com/f/page_viewforum/f_29/start_",
             "https://www.chineseinatlanta.com/f/page_viewforum/f_29/start_",
             "https://www.chineseinflorida.com/f/page_viewforum/f_29/start_",
             "https://www.dcchinaren.com/f/page_viewforum/f_29/start_"]

    for i in range(len(domains)):
        name = "all_job_postings_links_" + str(i) + ".csv"
        scrape_links(domains[i], 50, name)
    #print(scrape_job_post("https://rusrek.com/mall/priglashaem_zhenshchin_8091508"))
    #scrape_all_job_posts("massage_parlor_links.csv", "massage_parlor_posts.json")

    #scrape_all_job_posts("all_job_postings_links.csv", "all_job_postings_posts.json")