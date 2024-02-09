import requests
import json
from datetime import datetime, timedelta

API_KEY = 'PSPGHH6OJUGEPT7F'

class AlphaVantageWrapper:
    BASE_URL = 'https://www.alphavantage.co/query?'

    def week_articles(self, ticker):
        datetime_format = '%Y%m%dT%H%M'
        past_week = datetime.now() - timedelta(weeks=1)
        formatted_past_week = past_week.strftime(datetime_format)

        # Using default values for the other parameters
        url = f"{self.BASE_URL}function=NEWS_SENTIMENT&tickers={ticker}&time_from={formatted_past_week}&sort=RELEVANCE&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        return data
    
    def company_overview(self, ticker):
        url = f"{self.BASE_URL}function=OVERVIEW&symbol={ticker}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        return data
    
    def write_json(self, content):
        with open('data.json', 'w') as outfile:
            json.dump(content, outfile, indent=2)
    
test = AlphaVantageWrapper()
articles = test.week_articles('AAPL')
test.write_json(articles)