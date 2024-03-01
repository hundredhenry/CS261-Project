import requests
import json
from datetime import datetime, timedelta

API_KEY = 'PSPGHH6OJUGEPT7F'

class AlphaVantageWrapper:
    BASE_URL = 'https://www.alphavantage.co/query?'

    def week_articles(self, ticker):
        # Get the date from a week ago
        datetime_format = '%Y%m%dT%H%M'
        past_week = datetime.now() - timedelta(weeks=1)
        formatted_past_week = past_week.strftime(datetime_format)

        # Using default values for the other parameters
        url = f"{self.BASE_URL}function=NEWS_SENTIMENT&tickers={ticker}&time_from={formatted_past_week}&sort=LATEST&apikey={API_KEY}"
        print(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json()['feed']

            return articles
        except Exception as e:
            print(f"Error occurred: {e}")

            return None
    
    def company_overview(self, ticker):
        url = f"{self.BASE_URL}function=OVERVIEW&symbol={ticker}&apikey={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()["Description"]

            return data
        except Exception as e:
            print(f"Error occurred: {e}")

            return None