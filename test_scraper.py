import unittest
from unittest.mock import patch
import requests_mock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from scraper import scrape_links

class TestScraper(unittest.TestCase):

    def test_scrape_links_success(self):
        with requests_mock.Mocker() as m:
            test_url = "http://test.com"
            html_content = '''
            <html>
            <body>
                <a href="/link1">Link 1</a>
                <a href="http://test.com/link2">Link 2</a>
            </body>
            </html>
            '''
            m.get(test_url, text=html_content)
            links = scrape_links(test_url)
            self.assertEqual(len(links), 2)
            self.assertIn("/link1", links)
            self.assertIn("http://test.com/link2", links)

    def test_scrape_links_http_error(self):
        with requests_mock.Mocker() as m:
            test_url = "http://error.com"
            m.get(test_url, status_code=404)
            links = scrape_links(test_url)
            self.assertEqual(len(links), 0)

    def test_scrape_links_empty_page(self):
        with requests_mock.Mocker() as m:
            test_url = "http://empty.com"
            m.get(test_url, text="<html><body></body></html>")
            links = scrape_links(test_url)
            self.assertEqual(len(links), 0)

    def test_scrape_links_no_links(self):
        with requests_mock.Mocker() as m:
            test_url = "http://nolinks.com"
            m.get(test_url, text="<html><body><p>No links here</p></body></html>")
            links = scrape_links(test_url)
            self.assertEqual(len(links), 0)


if __name__ == '__main__':
    unittest.main()