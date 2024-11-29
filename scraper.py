import sqlite3
import urllib
import urllib.parse
import pandas as pd
import newspaper_scraper as nps
import spacy
import numpy

# Function to extract the domain (i.e., the newspaper/source) from the URL
from newsplease import NewsPlease


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
        print(f"Error scraping {url}: {e}")
        return None


# Function to scrape multicle articles and return a dataframe with relevant information
def scrape_articles(url_list):
    # Initialize an empty list to store scraped article data
    articles_data = []

    # Loop through each URL and scrape the article
    for url in url_list:
        article_data = scrape_article(url)
        if article_data:
            articles_data.append(article_data)

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(articles_data)

    return df


newspapers = [{"function": nps.DeBild(db_file='articles_bild.db'), "file": "articles_bild.de", "name": "Bild"},
              {"function": nps.DeWelt(db_file='articles_welt.db'), "file": "articles_welt.de", "name": "welt"}]


def scrape_all_newspapers():
    for newspaper in newspapers:
        with newspaper["function"] as news:
            news.index_articles_by_date_range('2023-01-01', '2023-01-02')  # CHANGE THE DATE HERE!!
            news.scrape_public_articles()


nlp = spacy.load("de_core_news_md")


def scrape_and_analyze(name):
    cnx = sqlite3.connect(name)  # Name is the file path to the database

    urls = pd.read_sql_query("SELECT * FROM {}".format("tblArticlesIndexed"),
                             cnx)  # We do a query that returns a dataframe from the table tblArticlesIndexed

    df = scrape_articles(urls['URL'].head())
    # docs = nlp.pipe(df['maintext'])
    # displacy.render(docs,style='ent', jupyter=True)


scrape_all_newspapers()
scrape_and_analyze("articles_welt.db")
