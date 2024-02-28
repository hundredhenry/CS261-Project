from alphavantage import AlphaVantageWrapper
from scraper import ArticleScraper
from sqlalchemy import create_engine, select, insert, delete, text
from website.models import User, Notification, Follow, Company, Article
from transformers import pipeline

engine = create_engine("mysql://sql8687211:iwcRTfjlEi@sql8.freemysqlhosting.net:3306/sql8687211")

class NewsSystem:
    def __init__(self):
        self.alpha_vantage = AlphaVantageWrapper()
        self.scraper = ArticleScraper()
        self.sentiment_pipeline = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")

    def get_sentiment(self, content):
        sentiment = self.sentiment_pipeline(content)

        return sentiment

    def get_companies(self, conn):
        companies = []

        # Get all companies from the database
        query = select(Company.stock_ticker)
        result = conn.execute(query)

        for row in result:
            companies.append(row[0])

        return companies
    
    def get_articles(self, ticker):
        conn = engine.connect()
        articles = []

        # Get all articles for the specified company
        query = select(Article).where(Article.stock_ticker == ticker)
        result = conn.execute(query)

        for row in result:
            articles.append({
                'title': row[0],
                'stock_ticker': row[1],
                'url': row[2],
                'time_published': row[6],
                'description': row[7],
                'banner_image': row[8],
                'source': row[3],
                'source_domain': row[4],
                'sentiment_label': row[9],
                'sentiment_score': row[10],
            })

        conn.close()
        return articles
    
    def update_companies(self):
        conn = engine.connect()
        companies = self.get_companies(conn)

        for ticker in companies:
            articles = self.collection(ticker)

            # Drop all articles for the current company
            query = delete(Article).where(Article.stock_ticker == ticker)
            conn.execute(query)
            conn.commit()

            # Insert all articles for the current company
            for article in articles:
                query = insert(Article).values(
                    title = article['title'],
                    stock_ticker = ticker,
                    source_name = article['source'],
                    source_domain = article['source_domain'],
                    url = article['url'],
                    published = article['time_published'],
                    description = article['description'],
                    banner_image = article['banner_image'],
                    sentiment_label = article['sentiment_label'],
                    sentiment_score = article['sentiment_score'],
                )
                conn.execute(query)
                conn.commit()
        conn.close()

    def collection(self, ticker):
        articles = self.alpha_vantage.week_articles(ticker)
        filtered = []
        
        for article in articles:
            meta_desc = self.scraper.get_meta_desc(article['url'])

            if meta_desc == None:
                sentiment = self.get_sentiment(article['title'])
            else:
                sentiment = self.get_sentiment(meta_desc)
            
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
system.update_companies()
print(system.get_articles('AAPL'))