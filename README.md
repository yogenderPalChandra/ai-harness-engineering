# Simple Python Web Scraper

This project provides a simple Python web scraper that fetches a given URL and extracts all hyperlinks from the page.

## Features

- Fetches web pages using `requests`.
- Parses HTML content using `BeautifulSoup`.
- Extracts all `href` attributes from `<a>` tags.
- Basic error handling for HTTP requests.

## Installation

1. Clone the repository (if applicable, otherwise just save `scraper.py` and `test_scraper.py`):

2. Install the required Python packages:

   ```bash
   pip install requests beautifulsoup4 requests-mock
   ```

## Usage

To run the scraper, execute the `scraper.py` file. By default, it scrapes `http://quotes.toscrape.com/`.

```bash
python scraper.py
```

To scrape a different URL, you can modify the `target_url` variable in `scraper.py`.

### `scrape_links(url)` function

This function takes a URL as input and returns a list of strings, where each string is a URL found on the page.

```python
from scraper import scrape_links

url = "https://www.example.com"
links = scrape_links(url)
for link in links:
    print(link)
```

## Running Tests

Unit tests are provided to ensure the scraper works as expected. These tests use `requests-mock` to avoid making actual network requests.

To run the tests, execute the `test_scraper.py` file:

```bash
python test_scraper.py
```

## Project Structure

- `scraper.py`: The main web scraping logic.
- `test_scraper.py`: Unit tests for the scraper.
- `README.md`: This documentation file.
