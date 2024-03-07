import requests
import json
from datetime import datetime, timedelta

API_KEY = 'PSPGHH6OJUGEPT7F'

class AlphaVantageWrapper:
    BASE_URL = 'https://www.alphavantage.co/query?'

    def day_articles(self, ticker, date):
        # Get the date today and formatted
        datetime_format = '%Y%m%dT%H%M'
        formatted_date = date.strftime(datetime_format)
        day_after = date + timedelta(days=1)
        formatted_day_after = day_after.strftime(datetime_format)

        # Using default values for the other parameters
        url = f"{self.BASE_URL}function=NEWS_SENTIMENT&tickers={ticker}&time_from={formatted_date}&time_to={formatted_day_after}&sort=LATEST&apikey={API_KEY}"
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