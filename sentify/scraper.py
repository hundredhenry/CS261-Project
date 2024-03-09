import logging
import random
import time
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
]

class ArticleScraper:
    """
    A class for scraping article data from URLs.

    Attributes:
        user_agents (list): A list of user agents to be used for making requests.
        session (requests.Session): A session object for making HTTP requests.

    Methods:
        __init__(self, user_agents=None): Initialises the ArticleScraper object.
        __get_html(self, url, referer='https://www.google.com', delay=1): Retrieves the HTML content of a given URL.
        get_meta_desc(self, url): Retrieves the meta description from the given URL.
    """
    def __init__(self, user_agents=None):
        self.user_agents = user_agents or USER_AGENTS
        self.session = requests.Session()

    def __get_html(self, url, referer='https://www.google.com', delay=1):
        """
        Retrieves the HTML content of a given URL.

        Args:
            url (str): The URL to retrieve the HTML content from.
            referer (str, optional): The referer URL. Defaults to 'https://www.google.com'.
            delay (int, optional): The delay in seconds before making the request. Defaults to 1.

        Returns:
            str: The HTML content of the URL, or None if an error occurred.
        """
        if delay:
            time.sleep(0.5)
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Referer': referer,
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            logging.error(f"An error occurred: {err}")
        return None

    def get_meta_desc(self, url):
        """
        Retrieves the meta description from the given URL.

        Args:
            url (str): The URL to scrape the meta description from.

        Returns:
            str or None: The content of the meta description if found, None otherwise.
        """
        html = self.__get_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                return meta_tag.get('content')
            else:
                return None
        else:
            return None