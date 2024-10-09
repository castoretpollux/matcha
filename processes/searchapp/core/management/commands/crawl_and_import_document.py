from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from core.models import Document, Part
from lib.vectorize import vectorize
from lib.tokenize import extract_parts
from lib.utils import generate_summary
import json
import os

from urllib.parse import urljoin
import urllib.robotparser
import requests

from bs4 import BeautifulSoup  # type: ignore


class CommandCrawler:

    def __init__(self, base_url, urls=None, visited_urls=None):
        self.base_url = base_url
        self.visited_urls = visited_urls or []  # List to store visited URLs
        self.urls_to_visit = urls or []  # List to store URLs to visit
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(urljoin(base_url, "robots.txt"))
        self.robot_parser.read()

    def download_url(self, url):
        try:
            resp = requests.get(url, verify=False, timeout=20.0, headers=self.headers)  # NOSONAR
            status_code = resp.status_code
        except Exception:
            status_code = 'xxx'
        if status_code == 200:
            return resp.text
        return None

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

    def crawl(self, crawlurl, namespace, stdout):
        if not self.robot_parser.can_fetch("*", crawlurl):
            return
        html = self.download_url(crawlurl)  # Download the HTML content of the webpage
        if html is None:  # sth bad happened...
            print("crawling", crawlurl, "XXXXXXX KO")
            return
        else:
            print("crawling", crawlurl, "OK")
        soup = BeautifulSoup(html, 'html.parser')  # Create a BeautifulSoup object for parsing the HTML
        for url in self.get_linked_urls(crawlurl, soup):
            self.add_url_to_visit(url, crawlurl)  # Add the linked URLs to the list of URLs to visit
        self.save_document(self.get_text(soup, crawlurl), namespace)  # Extract and store the text data from the webpage
        # log progress
        stdout.write(f'Visited: {len(self.visited_urls)}')
        stdout.write(f'To visit: {len(self.urls_to_visit)}')
        urls_nb = len(self.visited_urls) + len(self.urls_to_visit)
        stdout.write(f'Progress: {len(self.visited_urls)} / {urls_nb}')
        # save the urls and visited urls to the file
        with open(f'{namespace}.json', 'w') as file:
            data = {
                'urls': self.urls_to_visit,
                'visited_urls': self.visited_urls
            }
            json.dump(data, file)

    def save_document(self, text_obj, namespace):
        txt = text_obj['text']
        vector = vectorize(txt)
        document = Document(
            title=text_obj['title'],
            namespace=namespace,
            content=text_obj['text'],
            summary=generate_summary(txt),
            url=text_obj['url'],
            embedding=vector
        )
        document.save()

        parts = extract_parts(text_obj['text'], size=settings.PART_SIZE, overlap=settings.PART_OVERLAP)

        for content in parts:
            vector = vectorize(content)
            part = Part(
                document=document,
                content=content,
                embedding=vector
            )
            part.save()

    def run(self, namespace, max_requests, stdout):
        while self.urls_to_visit and len(self.visited_urls) < max_requests:
            url = self.urls_to_visit.pop(0)  # Get the next URL to crawl
            self.visited_urls.append(url)  # Mark the URL as visited
            try:
                self.crawl(url, namespace, stdout)  # Crawl the URL
            except Exception as e:
                print(f'Failed to crawl: {url}')  # Print an error message if crawling fails
                print(repr(e))


class Command(BaseCommand):
    help = 'Crawl website and import document to database'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('url', type=str, help='URL to crawl')
        parser.add_argument('namespace', type=str, help='Namespace of the document')
        parser.add_argument('max_requests', type=int, help='Maximum requests to make', default=1000)

    def handle(self, *args, **kwargs):
        url = kwargs['url']
        namespace = kwargs['namespace']
        max_requests = kwargs.get('max_requests', 1000)
        # log the url and namespace
        self.stdout.write(f'URL: {url}')
        self.stdout.write(f'Namespace: {namespace}')

        # log crawl started
        self.stdout.write('Crawl started')

        # if file with the name of the namespace exists continue the crawl with data from the file
        if os.path.exists(f'{namespace}.json'):
            # log file founded continue crawl
            self.stdout.write('File founded continue crawl')
            # get urls and visited urls from the file
            with open(f'{namespace}.json', 'r') as file:
                data = json.load(file)
                urls = data['urls']
                visited_urls = data['visited_urls']
                # Crawl the website and transform the content to a document
                CommandCrawler(base_url=url, urls=urls, visited_urls=visited_urls).run(namespace, max_requests, self.stdout)
        else:
            # Create a new file with the name of the namespace
            with open(f'{namespace}.json', 'w') as file:
                data = {
                    'urls': [],
                    'visited_urls': []
                }
                json.dump(data, file)
            # Crawl the website and transform the content to a document
            CommandCrawler(base_url=url, urls=[url]).run(namespace, max_requests, self.stdout)

        # delete file with the name of the namespace
        os.remove(f'{namespace}.json')

        # log crawl ended
        self.stdout.write('Crawl ended')
