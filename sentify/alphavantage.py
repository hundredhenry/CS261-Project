import requests
from datetime import timedelta

API_KEY = 'PSPGHH6OJUGEPT7F'

class AlphaVantageWrapper:
    BASE_URL = 'https://www.alphavantage.co/query?'

    def day_articles(self, ticker, date):
        """
        Retrieves news articles for a given ticker and date.

        Args:
            ticker (str): The ticker symbol of the stock.
            date (datetime.date): The date for which to retrieve news articles.

        Returns:
            list: A list of news articles for the specified ticker and date.
                Each article is represented as a dictionary.

        Raises:
            requests.exceptions.RequestException: If an error occurs while making the API request.

        """
        # Get the date today and formatted
        datetime_format = '%Y%m%dT%H%M'
        formatted_date = date.strftime(datetime_format)
        day_after = date + timedelta(days=1)
        formatted_day_after = day_after.strftime(datetime_format)

        # Using default values for the other parameters
        url = f"{self.BASE_URL}function=NEWS_SENTIMENT&tickers={ticker}&time_from={formatted_date}&time_to={formatted_day_after}&sort=LATEST&apikey={API_KEY}"
        print(url)
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            articles = response.json()['feed']

            return articles
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")

            return None

    def company_overview(self, ticker):
        """
        Retrieves the company overview for a given ticker symbol.

        Args:
            ticker (str): The ticker symbol of the company.

        Returns:
            str: The company overview description.

        Raises:
            requests.exceptions.RequestException: If an error occurs while making the API request.
        """
        url = f"{self.BASE_URL}function=OVERVIEW&symbol={ticker}&apikey={API_KEY}"
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()["Description"]

            return data
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")

            return None
