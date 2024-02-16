import requests
import json
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
            return "No content"
                
# Example usage
scraper = ArticleScraper()
print("Attempting to scrape a BBC article")
bbcdesc = scraper.scrape_bbc("https://www.bbc.co.uk/news/business-68282487")
bbcdesc2 = scraper.get_meta_desc("https://www.bbc.co.uk/news/business-68282487")
print("1: " + bbcdesc)
print("2: " + bbcdesc2)

print("Attempting to scrape a sky article")
skydesc = scraper.scrape_bbc("https://news.sky.com/story/poisoned-jailed-and-mysterious-fall-from-window-whats-happened-to-vladimir-putins-most-vocal-critics-13066825")
skydesc2 = scraper.get_meta_desc("https://news.sky.com/story/poisoned-jailed-and-mysterious-fall-from-window-whats-happened-to-vladimir-putins-most-vocal-critics-13066825")
print("1: " + skydesc)
print("2: " + skydesc2)

print("Attempting to scrape a Guardian article")
# guardiandesc = scraper.scrape_bbc("https://www.theguardian.com/uk-news/2024/feb/16/ministers-warned-over-risk-of-violence-and-arson-at-essex-wethersfield-airbase-holding-asylum-seekers")
guardiandesc2 = scraper.get_meta_desc("https://www.theguardian.com/uk-news/2024/feb/16/ministers-warned-over-risk-of-violence-and-arson-at-essex-wethersfield-airbase-holding-asylum-seekers")
# print("1: " + guardiandesc)
print("2: " + guardiandesc2)

# Testing some typical sites from alphavantage

print("Attempting to scrape an Investors.com article")
# investorsdesc = scraper.scrape_bbc("https://www.investors.com/news/technology/apple-stock-ai-strategy-could-include-siri-2/")
investorsdesc2 = scraper.get_meta_desc("https://www.investors.com/news/technology/apple-stock-ai-strategy-could-include-siri-2/")
# print("1: " + investorsdesc)
print("2: " + investorsdesc2)
# Investors.com giving 403 on request, forbidding us from entering. Need to implement a workaround?

print("Attempting to scrape a marketwatch.com article")
marketwarchdesc = scraper.get_meta_desc("https://www.marketwatch.com/story/meta-apple-are-squabbling-again-over-advertisers-1c8ab2b8")
print(marketwarchdesc)
# Works

print("Attempting to scrape a fool.com article")
fooldesc = scraper.get_meta_desc("https://www.fool.com/investing/2024/02/14/dan-ives-sees-over-40-upside-in-this-artificial-in/")
print(fooldesc)
# Works

print("Attempting to scrape a benzinga article")
benzingadesc = scraper.get_meta_desc("https://www.benzinga.com/news/24/02/37150573/faster-smarter-iphones-and-macs-are-coming-apples-upcoming-chips-will-get-major-ai-boost")
print(benzingadesc)
# Works

