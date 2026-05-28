'''A simple web scraper using requests and BeautifulSoup.'''

import requests
from bs4 import BeautifulSoup

def scrape_links(url):
    """Fetches a URL and returns a list of all links found on the page."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        links.append(a_tag['href'])
    return links

if __name__ == "__main__":
    target_url = "http://quotes.toscrape.com/"  # A sample website to scrape
    print(f"Scraping links from: {target_url}")
    all_links = scrape_links(target_url)
    for link in all_links:
        print(link)