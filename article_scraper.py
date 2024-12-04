#article_scraper.py

import sqlite3
import urllib.parse
import pandas as pd
from newsplease import NewsPlease
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # For progress tracking

# Set up logging for error handling
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)


# Function to extract the domain (i.e., the newspaper/source) from the URL
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
        logging.error(f"Error scraping {url}: {e}")
        return None


# Function to scrape articles in parallel
def scrape_articles_parallel(url_list):
    articles_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_article, url): url for url in url_list}

        # Use tqdm to track the progress of the scraping
        for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc="Scraping articles"):
            url = future_to_url[future]
            try:
                article_data = future.result()
                if article_data:
                    articles_data.append(article_data)
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")
    return pd.DataFrame(articles_data)


# Function to scrape articles in batches
def scrape_articles_in_batches(url_list, batch_size=1000):
    all_data = []
    for i in range(0, len(url_list), batch_size):
        batch = url_list[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1}/{len(url_list) // batch_size + 1}")
        df_batch = scrape_articles_parallel(batch)
        all_data.append(df_batch)
    return pd.concat(all_data, ignore_index=True)


# Function to filter URLs that have already been processed
def filter_unprocessed_urls(url_list, processed_file='articles_24.csv'):
    try:
        processed_urls = pd.read_csv(processed_file)['url'].tolist()
        return [url for url in url_list if url not in processed_urls]
    except FileNotFoundError:
        # No processed file exists yet
        return url_list


# Function to scrape and analyze articles
def scrape_and_analyze(db_name):
    cnx = sqlite3.connect(db_name)
    urls = pd.read_sql_query("SELECT * FROM tblArticlesIndexed", cnx)
    print(f"Total URLs in the database: {len(urls)}")  # Check the total number of URLs

    urls_to_process = filter_unprocessed_urls(urls['URL'])
    print(f"Remaining URLs to scrape: {len(urls_to_process)}")

    df = scrape_articles_in_batches(urls_to_process, batch_size=1000)
    print(f"Scraped articles: {len(df)}")  # Check how many articles were scraped

    # Save the dataframe to CSV
    df.to_csv('articles_24.csv', mode='a', index=False, header=not pd.io.common.file_exists('articles_24.csv'))


# Call the function with your database
scrape_and_analyze("articles_24.db")
