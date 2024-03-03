from alphavantage import AlphaVantageWrapper
from scraper import ArticleScraper
from sqlalchemy import select, insert, delete, update, bindparam
from website import db
from website.models import User, Notification, Follow, Company, Article
from transformers import pipeline
from datetime import date

class NewsSystem:
    def __init__(self):
        self.alpha_vantage = AlphaVantageWrapper()
        self.scraper = ArticleScraper()
        self.sentiment_pipeline = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")
        self.companies = self.get_companies()

    def get_sentiment(self, content):
        sentiment = self.sentiment_pipeline(content)

        return sentiment

    def get_companies(self):
        # Get all companies from the database
        query = select(Company.stock_ticker)
        result = db.session.execute(query)
        companies = result.fetchall()
        companies = [company[0] for company in companies]

        return companies

    def get_last_updated(self, ticker):
        # Get the last updated date for the specified company
        query = select(Company.last_updated).where(Company.stock_ticker == ticker)
        result = db.session.execute(query)
        update_date = result.fetchone()[0]

        return update_date

    def update_companies_desc(self):
        for ticker in self.companies:
            # Get the last updated date for the current company
            last_updated = self.get_last_updated(ticker)

            # Check if the current company has been updated
            if last_updated > date(1970, 1, 1):
                continue

            # Get the description for the current company
            desc = self.alpha_vantage.company_overview(ticker)

            # Update the description for the current company
            query = update(Company).where(Company.stock_ticker == ticker).values(description = desc)
            db.session.execute(query)
            db.session.commit()

    def update_companies(self):
        for ticker in self.companies:
            try:
                # Get the last updated date for the current company
                last_updated = self.get_last_updated(ticker)

                # Check if the current company has been updated today
                if last_updated == date.today():
                    continue

                articles = self.collection(ticker)
                positive = 0
                total = 0

                # Check if there are no articles for the current company
                if not articles:
                    continue

                # Drop all articles for the current company in the database
                query = delete(Article).where(Article.stock_ticker == ticker)
                db.session.execute(query)

                # Prepare the SQL statement
                stmt = insert(Article).values(
                    title=bindparam('title'),
                    stock_ticker=bindparam('stock_ticker'),
                    source_name=bindparam('source_name'),
                    source_domain=bindparam('source_domain'),
                    url=bindparam('url'),
                    published=bindparam('published'),
                    description=bindparam('description'),
                    banner_image=bindparam('banner_image'),
                    sentiment_label=bindparam('sentiment_label'),
                    sentiment_score=bindparam('sentiment_score')
                )

                # Execute the statement for all data
                db.session.execute(stmt, articles)

                # Update the total and positive ratings for the current company
                total = len(articles)
                positive = sum(1 for article in articles
                               if article['sentiment_label'] == 'POSITIVE')

                # Update the positive rating for the current company
                if total != 0:
                    positive_rating = (positive / total) * 100
                    query = update(Company).where(
                        Company.stock_ticker == ticker).values(
                            positive_rating = positive_rating)
                    db.session.execute(query)

                # Update the last updated date for the current company
                query = update(Company).where(
                    Company.stock_ticker == ticker).values(
                        last_updated = date.today())
                db.session.execute(query)

                # Send notifications to all users following the current company
                self.send_notifications(ticker)

                # Commit the changes to the database
                db.session.commit()
            except Exception as e: # need to be more specific
                print(e)
                db.session.rollback()

    def collection(self, ticker):
        # Get articles for the specified company
        articles = self.alpha_vantage.week_articles(ticker)
        filtered = []

        if articles:
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
                    'stock_ticker': ticker,
                    'source_name': article['source'],
                    'source_domain': article['source_domain'],
                    'url': article['url'],
                    'published': article['time_published'],
                    'description': meta_desc,
                    'banner_image': article['banner_image'],
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
        return max_ticker == ticker

    def send_notifications(self, ticker):
        # Get all users following the specified company
        query = select(User.user_id).join(
            Follow, User.user_id == Follow.user_id).where(
                Follow.stock_ticker == ticker)
        result = db.session.execute(query)

        if result:
            for row in result:
                # Send a notification to the current user
                query = insert(Notification).values(
                    user_id = row[0],
                    message = f"New articles available for {ticker}!")
                db.session.execute(query) # commit after?!
