import sqlite3
import urllib
import urllib.parse
import pandas as pd
import newspaper_scraper as nps
import csv
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to extract the domain (i.e., the newspaper/source) from the URL
from newsplease import NewsPlease

# Set up logging for error handling
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

def extract_newspaper(url):
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    return domain.replace('www.', '')  # Clean up 'www.' if present


# Function to scrape an article from a URL and return relevant information
def scrape_article(url):
    try:
        article = NewsPlease.from_url(url)
        return {
            'title': article.title,
            'authors': article.authors,
            'date_publish': article.date_publish,
            'maintext': article.maintext,
            'url': url,
            'newspaper': extract_newspaper(url)  # Add newspaper information
        }
    except Exception as e:
        # Return None if there's any error (e.g., 404, timeout)
        #print(f"Error scraping {url}: {e}")
        logging.error(f"Error scraping {url}: {e}")
        return None


# Function to scrape multicle articles and return a dataframe with relevant information
def scrape_articles(url_list):
    # Initialize an empty list to store scraped article data
    articles_data = []
    url_count = 0
    total_urls = len(url_list)

    # Loop through each URL and scrape the article
    for url in url_list:
        print(f"{url_count + 1}/{total_urls}")
        url_count += 1
        article_data = scrape_article(url)
        if article_data:
            articles_data.append(article_data)

    # Convert the list of dictionaries to a pandas DataFrame

    df = pd.DataFrame(articles_data)
    #df.to_csv('arcitles1.csv')

    return df


newspapers = [{"function": nps.DeBild(db_file='articles_24.db'), "file": "articles_bild.de", "name": "Bild"},
              {"function": nps.DeWelt(db_file='articles_24.db'), "file": "articles_welt.de", "name": "welt"}]

# YEAR-MONTH-DAY
def scrape_all_newspapers():
    for newspaper in newspapers:
        with newspaper["function"] as news:
            news.index_articles_by_date_range('2024-01-01', '2024-6-01')  # CHANGE THE DATE HERE!!
            news.scrape_public_articles()


#nlp = spacy.load("de_core_news_md")


def scrape_and_analyze(name):
    cnx = sqlite3.connect(name)  # Name is the file path to the database

    urls = pd.read_sql_query("SELECT * FROM {}".format("tblArticlesIndexed"),
                             cnx)  # We do a query that returns a dataframe from the table tblArticlesIndexed
    print(f"Amount of URLs: {len(urls)}")  # Check the total number of URLs


    df = scrape_articles(urls['URL'])  # Pass the entire column of URLs
    print(f"Scraped articles: {len(df)}")  # Check how many articles were scraped
    # Save the dataframe to CSV
    df.to_csv('articles_24.csv', index=False)
    #HERE The conversion?


#scrape_all_newspapers()
#41062/47787   6725 Articles missing from the Time frame due to errorwhile scraping
#41062 still enough sample size
scrape_and_analyze("articles_24.db")

