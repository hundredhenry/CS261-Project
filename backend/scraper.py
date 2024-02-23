import requests
import logging
import random
import time
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

# Need to add a list of user agents to randomise choice from, mimicing user behaviour
# Some github repos available but may be outdated
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/80.0.3987.149 Safari/537.36")
class ArticleScraper:
    def __init__(self):
        pass
    
    def __get_html(self, url, referer = None, delay = 1):
        # Added delay to mimic user behaviour if requesting from same site multiple times
        if delay:
            # Could be randomised if run into more 403s
            time.sleep(delay)
        headers = {
            'User-Agent': USER_AGENT,
            # Added referer to header to further mimic user
            # Could be randomised if run into more 403s
            'Referer': referer if referer else 'https://www.google.co.uk'
        }
        try:
            with requests.get(url, headers=headers, timeout=10) as response:
                if response.status_code == 403:
                    logging.warning(f"Access Denied with 403 Forbidden Error to {url}")
                return response.text
        except requests.RequestException as e:
            logging.error(f"Error during requests to {url} : {str(e)}")
            return None
        
    def get_meta_desc(self, url):
        # Get HTML
        html = self.__get_html(url)
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        # Find meta tag
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        # Check if tag found
        if meta_tag:
            return meta_tag.get('content')
        else:
            return "No content could be displayed"
                
# Example usage
scraper = ArticleScraper()
print("Attempting to scrape a BBC article")
print(scraper.get_meta_desc("https://www.bbc.co.uk/news/business-68282487"))