import json
import xlsxwriter
import pandas as pd
import pickle
import numpy as np
from bs4 import BeautifulSoup
import requests
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import codecs
import os
import re

"""
credit to Richard
"""
def extract_phone_numbers(text):
    # Define a regex pattern for matching US phone numbers and sequences of 10 digits
    phone_number_pattern = re.compile(r'\b(?:\+?1\s*[-.\s*]?)?(?:(?:\(\d{3}\))|(?:\d{3}))[-.\s*]?\d{3}[-.\s*]?\d{4}\b|\b\d{10}\b')

    # Find all matches in the text
    matches = phone_number_pattern.findall(text)

    return matches

def extract_emails(text):
    # Define a regex pattern for matching email addresses
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Find all matches in the text
    matches = email_pattern.findall(text)

    return matches

def init_soup(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
    except:
        raise Exception("Selenium Driver Exception")
    sleep(1)
    page_source = driver.page_source
    return BeautifulSoup(page_source, 'html.parser')

def scrape_list_view_page(url):
    print(url)
    soup = init_soup(url)
    list_items = soup.select("div:not(.bid_box) > div.topic_list_detail")
    post_urls = []
    viewcounts = []
    titles = []
    #f = open(fname, "a")
    for item in list_items:
        href_div = item.select("div.topic_list_12")
        if len(href_div) > 0:
            a = href_div[0].find("a", href=True)
            if a is not None:
                post_urls.append(a['href'])
                titles.append(a.get_text())
                print(a['href'])
                print(a.get_text())
                read_count_span = item.select("span.read_count")
                #line = ""
                if len(read_count_span) > 0:
                    viewcounts.append(read_count_span[0].text.strip())
                    #line = a['href'] + "," + read_count_span[0].text.strip() + ",\"" + a.get_text() + "\"\n"

                else:
                    viewcounts.append(-1)
                    #line = a['href'] + "," + "-1" + ",\"" + a.get_text() + "\"\n"
                #print(line)
                #f.write(line)
    #f.close()
    #return len(list_items) > 3
    return post_urls, viewcounts, titles, len(list_items) > 3

def scrape_all_list_view_pages(domain, list_view_url, max_pages = 9999999):
    post_urls = []
    post_views = []
    post_titles = []
    i = 19230
    has_more_pages = True
    seg = domain.split(".")
    #fname = seg[1] + "_url.csv"
    while has_more_pages and i <= max_pages:
        #has_more_pages = scrape_list_view_page(domain + list_view_url + str(i) + ".html", fname)
        urls, viewcounts, titles, has_more_pages = scrape_list_view_page(domain + list_view_url + str(i) + ".html")
        if has_more_pages:
            post_urls += [domain + url for url in urls]
            post_views += viewcounts
            post_titles += titles
        print(has_more_pages)
        i += 15
        # while has_more_pages:
        # urls, viewcounts, titles, has_more_pages = scrape_list_view_page(domain + list_view_url + str(i) + ".html", fname)
        # urls, viewcounts, titles, has_more_pages = scrape_list_view_page("https://www.dcchinaren.com/f/page_viewforum/f_29/start_3480.html")



    return post_urls, post_views, post_titles


def save_job_post_html(url, save_directory):
    soup = init_soup(url)
    fname = url.split("/")[5]
    print(fname)
    current_dir = os.path.dirname(__file__)

    path = os.path.join(current_dir, save_directory)
    if not os.path.exists(path):
        os.mkdir(path)

    f = codecs.open(os.path.join(path, fname), "w+", "utf−8")
    f.write(soup.prettify())
    f.close()


def collect_data_point(soup):
    data = {"phone_numbers": [], "emails": []}

    title = soup.select("div.post_title")
    if len(title):
        data["title"] = title[0].text.strip()

    post_times = soup.select("div.post_time span")
    if len(post_times):
        time_text = post_times[0].text.split(":", 1)
        if (len(time_text) == 2):
            time_text = time_text[1].strip()
            time_text = re.sub(r'\s+', ' ', time_text)
            data["date_created"] = time_text

        # Is there a date modified?
        if len(post_times) > 1:
            time_text = post_times[1].text.split(":", 1)
            if (len(time_text) == 2):
                time_text = time_text[1].strip()
                time_text = re.sub(r'\s*,\s*', ' ', time_text)
                data["date_modified"] = time_text

    all_spans = soup.select("div.post_body span:has(span)")
    for span in all_spans:
        text = span.get_text(strip=True)
        attributes = text.split(':')
        if len(attributes) > 1:
            data[attributes[0]] = attributes[1]

    custom_content = soup.select("p.real-content")
    if len(custom_content):
        data["phone_numbers"] = extract_phone_numbers(custom_content[0].text)
        data["emails"] = extract_emails(custom_content[0].text)

    return data

def scrape_job_post(url):
    soup = init_soup(url)
    #save_job_post_html(url, soup.prettify(), "chinese_job_posts_sources")
    #data = collect_data_point(soup)
    #return data


def main():
    site_urls = [
             #"https://www.vegaschinaren.com",
             "https://www.chineseinla.com",
             #"https://www.chineseinsfbay.com",
             #"https://www.nychinaren.com",
             #"https://www.seattlechinaren.com",
             #"https://www.chineseinatlanta.com",
             #"https://www.chineseinflorida.com",
             #"https://www.dcchinaren.com"
            ]

    data_points_and_keywords = {
        "url" : "",
        "post_type" : "类型",
        "position_type" : "性质",
        "work_type" : "行业",
        "org_name" : "名称",
        "address" : "地址",
        "location" : "地点",
        "remote_or_not" : "是否支持远程工作",
        "phone_numbers" : "phone_numbers",
        "emails" : "emails",
        "title" : "title",
        "date_created" : "date_created",
        "date_modified" : "date_modified",
        "viewcount" : "",
    }

    all_posts = {point: [] for point, _ in data_points_and_keywords.items()}
    """
    for url in site_urls:
        post_urls, post_viewcounts = scrape_all_list_view_pages(url, "/f/page_viewforum/f_29/start_")

        print(len(post_urls))
        print(len(post_viewcounts))

        all_posts["url"] += post_urls
        all_posts["viewcount"] += post_viewcounts

        for job_post_url in post_urls:
            print("start scraping")
            scrape_job_post(job_post_url)
            
            data = scrape_job_post(job_post_url)

            for data_point, data_keyword in data_points_and_keywords.items():
                if data_keyword != "":
                    if data_keyword in data:
                        all_posts[data_point].append(data[data_keyword])
                    else:
                        if data_point == "phone_numbers" or data_point == "emails":
                            all_posts[data_point].append([])
                        else:
                            all_posts[data_point].append("")

            f = open("chinese_job_postings.json", "wb")
            obj = json.dumps(all_posts, indent=4, ensure_ascii=False).encode('utf8')
            f.write(obj)
            f.close()
            """


if __name__ == "__main__":
    main()
