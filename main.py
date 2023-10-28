"""
Web Scraper: Quote Database

This script fetches and stores quotes from a defunct website via the Wayback Machine.
The data is saved in a CSV format.

Usage: python scraper.py
"""

import requests
import json
from bs4 import BeautifulSoup
import csv
import time

def create_csv():
    """Create a new CSV file with headers."""
    with open('quotes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        quote_writer = csv.writer(csvfile)
        quote_writer.writerow(['Quote', 'Author', 'Author Summary'])


def process_url_chunk(url_chunk, start_idx=0):
    """Process a chunk of URLs starting from a specific index."""
    with open('quotes.csv', 'a', newline='', encoding='utf-8') as csvfile:
        quote_writer = csv.writer(csvfile)

        for idx, url in enumerate(url_chunk[start_idx:], start=start_idx):
            final_url = 'https://web.archive.org/web/' + url
            print(f"Processing URL {idx + 1} of {len(url_chunk)}: {final_url}")
            
            max_retries = 3
            retries = 0
            success = False

            while not success and retries < max_retries:
                try:
                    webpage = requests.get(final_url)
                    success = True
                except (requests.exceptions.ReadTimeout, requests.exceptions.ContentDecodingError,
                        requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:

                    retries += 1
                    print(f"Error while fetching URL {final_url}: {e}, retrying ({retries}/{max_retries})")
                    time.sleep(5)

            if not success:
                print(f"Failed to fetch URL {final_url} after {max_retries} retries")
                continue

            soup = BeautifulSoup(webpage.text, "html.parser")
            sqa_element = soup.find("a", {"class": "sqa"})

            if sqa_element is not None:
                author = sqa_element.text.split(' quotes')[0]
            else:
                print(f"Could not find author for URL: {final_url}")
                continue

            quotes = soup.find_all("font", {"class": "sqq"})
            author_summary_mu = soup.find("font", {"class": "mu"})
            author_summary_sqb = soup.find("font", {"class": "sqb"})

            if author_summary_mu is not None:
                author_summary_text = author_summary_mu.text.strip('"')
            elif author_summary_sqb is not None:
                author_summary_text = author_summary_sqb.text.strip()
            else:
                author_summary_text = ""

            for i in quotes:
                quote = i.text.strip().strip('\"')
                quote_writer.writerow([quote, author, author_summary_text])
                print(f"{quote} - {author}")

            print(f"Author found for URL {final_url}: {author}")
            time.sleep(1)


def get_all_urls():
    """Fetch all the URLs for quotes from the Wayback Machine."""
    wayback_url = 'https://web.archive.org/cdx/search/cdx?url=thinkexist.com/quotes/&matchType=prefix&output=json'
    wayback_urls = requests.get(wayback_url).text

    try:
        parse_url = json.loads(wayback_urls)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

    url_list = [parse_url[i][1] + '/' + parse_url[i][2] for i in range(1, len(parse_url))]
    return sorted(list(set(url_list)))


def main():
    url_list = get_all_urls()
    create_csv()
    process_url_chunk(url_list)


if __name__ == "__main__":
    main()
