from urllib.parse import urljoin
import requests

from bs4 import BeautifulSoup  # type: ignore


class Crawler:

    def __init__(self, base_url, urls=None):
        self.base_url = base_url
        self.visited_urls = []  # List to store visited URLs
        self.urls_to_visit = urls or []  # List to store URLs to visit
        self.text_data = []  # List to store extracted text data

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, soup):
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def get_text(self, soup, url):
        text_obj = {
            'title': soup.title.string,  # Extract the title of the webpage
            'text': soup.get_text().replace('\n', ' '),  # Extract the text content of the webpage
            'url': url  # Store the URL of the webpage
        }

        return text_obj

    def add_url_to_visit(self, url, crawlurl):
        if url and url != crawlurl and url not in self.visited_urls and url not in self.urls_to_visit and not url.endswith('.pdf') and url.startswith(self.base_url):
            self.urls_to_visit.append(url)  # Add the URL to the list of URLs to visit

    def crawl(self, crawlurl):
        html = self.download_url(crawlurl)  # Download the HTML content of the webpage
        soup = BeautifulSoup(html, 'html.parser')  # Create a BeautifulSoup object for parsing the HTML
        for url in self.get_linked_urls(crawlurl, soup):
            self.add_url_to_visit(url, crawlurl)  # Add the linked URLs to the list of URLs to visit
        self.text_data.append(self.get_text(soup, crawlurl))  # Extract and store the text data from the webpage

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)  # Get the next URL to crawl
            try:
                self.crawl(url)  # Crawl the URL
            except Exception as e:
                print(f'Failed to crawl: {url}')  # Print an error message if crawling fails
                print(repr(e))
            finally:
                self.visited_urls.append(url)  # Mark the URL as visited

        return self.text_data  # Return the extracted text data
