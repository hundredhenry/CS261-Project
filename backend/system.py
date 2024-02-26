from alphavantage import AlphaVantageWrapper
from scraper import ArticleScraper
from sentiment import SentimentAnalysis

class NewsSystem:
    def __init__(self):
        self.alpha_vantage = AlphaVantageWrapper()
        self.scraper = ArticleScraper()
        self.sentiment = SentimentAnalysis()

    def collection(self, ticker):
        articles = self.alpha_vantage.week_articles(ticker)
        filtered = []
        
        for article in articles:
            max_relevance = 0
            most_relevant_ticker = None
            stock_list = article['ticker_sentiment']

            # Find the most relevant stock
            for stock in stock_list:
                relevance_score = float(stock['relevance_score'])
                if relevance_score > max_relevance:
                    max_relevance = relevance_score
                    most_relevant_ticker = stock['ticker']

            # If the most relevant stock is the same as the input ticker, get the sentiment, else skip
            if most_relevant_ticker == ticker:
                meta_desc = self.scraper.get_meta_desc(article['url'])
                sentiment = self.sentiment.get_sentiment(meta_desc)
                
                # Append specified article details to the filtered list
                filtered.append({
                    'title': article['title'],
                    'url': article['url'],
                    'time_published': article['time_published'],
                    'description': meta_desc,
                    'banner_image': article['banner_image'],
                    'source': article['source'],
                    'source_domain': article['source_domain'],
                    'sentiment_label': sentiment[0]['label'],
                    'sentiment_score': sentiment[0]['score'],
                })

        return filtered

system = NewsSystem()
collection = system.collection('AAPL')

# Formatted output
for article in collection:
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Time Published: {article['time_published']}")
    print(f"Description: {article['description']}")
    print(f"Banner Image: {article['banner_image']}")
    print(f"Source: {article['source']}")
    print(f"Source Domain: {article['source_domain']}")
    print(f"Sentiment Label: {article['sentiment_label']}")
    print(f"Sentiment Score: {article['sentiment_score']}")
    print()