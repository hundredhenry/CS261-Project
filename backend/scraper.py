import requests
import json
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/80.0.3987.149 Safari/537.36")
class ArticleScraper:
    def __init__(self):
        pass

    def __get_html(self, url):
        headers = {'User-Agent': USER_AGENT}
        try:
            with requests.get(url, headers=headers, timeout=10) as response:
                return response.text
        except requests.RequestException as e:
            logging.error(f"Error during requests to {url} : {str(e)}")
            return None

    def scrape_bbc(self, url):
        html = self.__get_html(url)
        
        if html is None:
            return None
        try:
            parser = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logging.error(f"Error during parsing: {str(e)}")
            return None
        
        script = parser.find('script', {'type': 'application/ld+json'})
        if script is None:
            logging.warning(f"No script tag found in {url}")
            return None

        try:
            script_json = json.loads(script.string)
            return script_json['description']
        except json.JSONDecodeError as e:
            logging.error(f"Error during JSON parsing: {str(e)}")
            return None
                
# Example usage
scraper = ArticleScraper()
desc = scraper.scrape_bbc("https://www.bbc.co.uk/news/business-68282487")
print(desc)
