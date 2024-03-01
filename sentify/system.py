from alphavantage import AlphaVantageWrapper
from scraper import ArticleScraper
from sqlalchemy import create_engine, select, insert, delete, update
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

        if result:
            for row in result:
                companies.append(row[0])

        return companies
    
    def update_companies_desc(self):
        conn = engine.connect()
        companies = self.get_companies(conn)

        for ticker in companies:
            # Get the description for the current company
            desc = self.alpha_vantage.company_overview(ticker)

            # Update the description for the current company
            query = update(Company).where(Company.stock_ticker == ticker).values(description = desc)
            conn.execute(query)
            conn.commit()   

        # Close the connection
        conn.close()
    
    def update_companies(self):
        conn = engine.connect()
        companies = self.get_companies(conn)

        for ticker in companies:
            articles = self.collection(ticker)
            positive = 0
            total = 0

            # Drop all articles for the current company
            try:
                query = delete(Article).where(Article.stock_ticker == ticker)
                conn.execute(query)
                conn.commit()
            except Exception as e:
                print(f"Error occurred: {e}")

            # Insert all articles for the current company
            for article in articles:
                try:
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
                        sentiment_score = article['sentiment_score']
                    )
                    conn.execute(query)
                    conn.commit()

                    # Update the total and positive ratings for the current company
                    total += 1
                    if article['sentiment_label'] == 'POSITIVE':
                        positive += 1
                except Exception as e:
                    print(f"Error occurred: {e}")
            
            # Update the positive rating for the current company
            if total != 0:
                positive_rating = (positive / total) * 100
                query = update(Company).where(Company.stock_ticker == ticker).values(positive_rating = positive_rating)
                conn.execute(query)
                conn.commit()

            # Send notifications to all users following the current company
            self.send_notifications(ticker, conn)
        
        # Close the connection
        conn.close()

    def collection(self, ticker):
        # Get articles for the specified company
        articles = self.alpha_vantage.week_articles(ticker)
        filtered = []

        if articles == None:
            return None
        
        for article in articles:
            # Check if the current article is the most relevant in the article
            if not self.most_relevant(ticker, article):
                continue

            # Get the meta description for the current article
            meta_desc = self.scraper.get_meta_desc(article['url'])

            # Get the sentiment for the current article
            if meta_desc:
                sentiment = self.get_sentiment(meta_desc)
            else:
                sentiment = self.get_sentiment(article['title'])
            
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
    
    def most_relevant(self, ticker, article):
        tickers = article['ticker_sentiment']
        max_ticker = None
        max_relevance = 0

        # Find the most relevant ticker
        for t in tickers:
            if float(t['relevance_score']) > float(max_relevance):
                max_ticker = t['ticker']
                max_relevance = t['relevance_score']
        
        # Check if the most relevant ticker is the specified company
        if max_ticker == ticker:
            return True
        
        return False
        
    def send_notifications(self, ticker, conn):
        # Get all users following the specified company
        query = select(User.id).join(Follow, User.id == Follow.userID).where(Follow.stock_ticker == ticker)
        result = conn.execute(query)

        if result:
            for row in result:
                # Send a notification to the current user
                query = insert(Notification).values(userID = row[0], message = f"New articles available for {ticker}!")
                conn.execute(query)
                conn.commit()

System = NewsSystem()
System.update_companies_desc()
System.update_companies()