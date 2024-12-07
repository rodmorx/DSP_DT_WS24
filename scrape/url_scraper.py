#article_scraper.py

import sqlite3
import newspaper_scraper as nps

# Define newspapers and their associated scraper functions
newspapers = [
    {"function": nps.DeBild(db_file='articles_24.db'), "name": "Bild"},
    {"function": nps.DeWelt(db_file='articles_24.db'), "name": "Welt"}
]

# YEAR-MONTH-DAY
def scrape_all_newspapers():
    """
    Scrape URLs from different newspapers and store them in the database.
    """
    for newspaper in newspapers:
        print(f"Scraping articles from {newspaper['name']}...")
        with newspaper["function"] as news:
            news.index_articles_by_date_range('2024-01-01', '2024-06-01')  # Adjust the date range as needed
            news.scrape_public_articles()
    print("Scraping and indexing of URLs completed!")

if __name__ == "__main__":
    scrape_all_newspapers()
