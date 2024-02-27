import requests
import logging
import random
import time
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
]

class ArticleScraper:
    def __init__(self, user_agents=None):
        self.user_agents = user_agents or USER_AGENTS
        self.session = requests.Session()
    
    def __get_html(self, url, referer='https://www.google.com', delay=1):
        if delay:
            self.__dynamic_delay()
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Referer': referer,
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None

    def __dynamic_delay(self):
        time.sleep(random.uniform(0.5, 3.0))

    def get_meta_desc(self, url):
        html = self.__get_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                return meta_tag.get('content')
            else:
                return "Description not found."
        else:
            return "Failed to retrieve HTML content."