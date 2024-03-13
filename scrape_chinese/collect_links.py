import json
import xlsxwriter
import pandas as pd
import utility

def main():
    site_urls = [

             "https://www.nychinaren.com",
            "https://www.chineseinsfbay.com",
        # "https://www.seattlechinaren.com",
        #"https://www.chineseinla.com",
        # "https://www.dcchinaren.com",
        # "https://www.chineseinatlanta.com",
        # "https://www.chineseinflorida.com",
        # "https://www.vegaschinaren.com",
            ]

    for url in site_urls:
        print(url)
        post_urls, post_viewcounts, titles = utility.scrape_all_list_view_pages(url, "/f/page_viewforum/f_29/start_")
        print(len(post_urls))
        print(len(post_viewcounts))
        print(len(titles))
        df = pd.DataFrame.from_dict({"url": post_urls, "view_count":post_viewcounts, "title":titles })

        seg = url.split(".")
        fname = seg[1] + "_url.csv"
        df.to_csv(fname, index=False)





if __name__ == "__main__":
    main()
