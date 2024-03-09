"""
This module defines the NewsSystem class which is responsible for managing the news articles and sentiment analysis for a list of companies. 

The NewsSystem class has methods to:
- Calculate sentiment of given content
- Retrieve a list of all companies from the database
- Update the description for each company in the system
- Update the sentiment ratings and articles for all companies in the system
- Retrieve and filter articles for a specified company and date
- Determine the most relevant ticker for a given article
- Send notifications to all users following a specified company
- Retrieve and update the companies' data for the past 7 days

This module uses the AlphaVantageWrapper class to interact with the Alpha Vantage API, the ArticleScraper class to scrape articles, and the Hugging Face's pipeline for sentiment analysis.

Dependencies:
- SQLAlchemy for database operations
- AlphaVantageWrapper for Alpha Vantage API interactions
- ArticleScraper for article scraping
- Hugging Face's pipeline for sentiment analysis
"""

from datetime import date, timedelta

from alphavantage import AlphaVantageWrapper
from scraper import ArticleScraper
from sqlalchemy import select, insert, bindparam
from sqlalchemy.exc import SQLAlchemyError
from website import db, socketio
from website.models import (User, Notification, Follow, Company,
                            Article, SentimentRating, Topic, ArticleTopic)
from transformers import pipeline
from flask import current_app

class NewsSystem:
    """
    This class represents a system for managing news articles and sentiment analysis for a list of companies.

    The NewsSystem class provides methods to:
    - Calculate sentiment of given content
    - Retrieve a list of all companies from the database
    - Update the description for each company in the system
    - Update the sentiment ratings and articles for all companies in the system
    - Retrieve and filter articles for a specified company and date
    - Determine the most relevant ticker for a given article
    - Send notifications to all users following a specified company
    - Retrieve and update the companies' data for the past 7 days

    Attributes:
    - alpha_vantage (AlphaVantageWrapper): An instance of the AlphaVantageWrapper class for interacting with the Alpha Vantage API.
    - scraper (ArticleScraper): An instance of the ArticleScraper class for scraping articles.
    - sentiment_pipeline (pipeline): A Hugging Face's pipeline for sentiment analysis.
    - companies (list): A list of stock tickers representing the companies.

    Note: This class assumes the existence of a SQLAlchemy session named `db.session` and a Flask-SocketIO instance named `socketio`.
    """
    def __init__(self):
        self.alpha_vantage = AlphaVantageWrapper()
        self.scraper = ArticleScraper()
        self.sentiment_pipeline = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")
        self.companies = self.get_companies()

    def get_sentiment(self, content):
        """
        Calculates the sentiment of the given content.

        Parameters:
        content (str): The content for which sentiment needs to be calculated.

        Returns:
        str: The sentiment of the content.
        """
        sentiment = self.sentiment_pipeline(content)

        return sentiment

    def get_companies(self):
        """
        Retrieves a list of all companies from the database.

        Returns:
            list: A list of stock tickers representing the companies.
        """
        companies = [company.stock_ticker for company in Company.query.all()]
        return companies

    def update_companies_desc(self):
        """
        Updates the description for each company in the system.

        This method iterates through the list of companies and checks if a description
        is already present for each company. If a description is not found, it retrieves
        the description using the Alpha Vantage API and updates the database with the new
        description.

        Note: This method assumes that the `Company` model has a `description` attribute
        and that the `alpha_vantage` object has a `company_overview` method.

        Returns:
            None
        """
        for ticker in self.companies:
            # Get the description for the company
            result = Company.query.filter_by(stock_ticker=ticker).first()

            # If there is a description for the company
            if result.description is not None:
                continue

            # Get the description for the current company
            desc = self.alpha_vantage.company_overview(ticker)

            # Update the description for the current company
            if desc:
                result.description = desc
                db.session.commit()

    def update_companies(self, date=date.today() - timedelta(days=1)):
        """
        Update the sentiment ratings and articles for all companies in the system.

        Args:
            date (datetime.date, optional): The date for which to update the sentiment ratings and articles.
                Defaults to the previous day.

        Raises:
            SQLAlchemyError: If there is an error executing the database queries.

        Returns:
            None
        """
        for ticker in self.companies:
            try:
                # Check if there is a Sentiment Rating for the current company
                result = SentimentRating.query.filter_by(stock_ticker=ticker, date=date).first()

                if result:
                    print(f"Sentiment rating already exists for {ticker} on {date}")
                    continue

                articles = self.collection(ticker, date)
                positive = 0
                total = 0

                # Check if there are no articles for the current company
                if not articles:
                    continue
                    
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

                # Insert article topics for each article
                for article in articles:
                    for topic in article['topics']:
                        topic_instance = Topic.query.filter_by(topic=topic['topic']).first()
                        topic_id = topic_instance.id if topic_instance else None

                        article_instance = Article.query.filter_by(url=article['url']).first()
                        article_id = article_instance.id if article_instance else None

                        article_topic = ArticleTopic(article_id=article_id, topic_id=topic_id)
                        db.session.add(article_topic)
                # Update the total and positive ratings for the current company
                total = len(articles)
                positive = sum(1 for article in articles
                               if article['sentiment_label'] == 'POSITIVE')

                # Update the positive rating for the current company
                if total != 0:
                    positive_rating = int((positive / total) * 100)
                    query = insert(SentimentRating).values(
                        stock_ticker=ticker, date=date, rating=positive_rating)
                    db.session.execute(query)

                # Send notifications to all users following the current company
                self.send_notifications(ticker)

                # Commit the changes to the database
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                
    def collection(self, ticker, date):
        """
        Retrieves and filters articles for the specified company and date.

        Args:
            ticker (str): The ticker symbol of the company.
            date (str): The date for which articles are to be retrieved.

        Returns:
            list: A list of dictionaries containing filtered article details,
            including title, stock ticker, source name, source domain, URL,
            publication date, description, topics, banner image, sentiment label, and sentiment score.
        """
        # Get articles for the specified company
        articles = self.alpha_vantage.day_articles(ticker, date)
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

                top_topics = sorted(article['topics'], key=lambda x: x['relevance_score'], reverse=True)[:3]

                # Append specified article details to the filtered list
                filtered.append({
                    'title': article['title'],
                    'stock_ticker': ticker,
                    'source_name': article['source'],
                    'source_domain': article['source_domain'],
                    'url': article['url'],
                    'published': article['time_published'],
                    'description': meta_desc,
                    'topics': top_topics,
                    'banner_image': article['banner_image'],
                    'sentiment_label': sentiment[0]['label'],
                    'sentiment_score': sentiment[0]['score'],
                })

        return filtered

    def most_relevant(self, ticker, article):
        """
        Determines the most relevant ticker for a given article.

        Args:
            ticker (str): The specified company ticker.
            article (dict): The article containing ticker sentiment information.

        Returns:
            bool: True if the most relevant ticker is the specified company, False otherwise.
        """
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
        """
        Sends notifications to all users following the specified company.

        Args:
            ticker (str): The stock ticker symbol of the company.

        Returns:
            None
        """
        with current_app.app_context():
            # Get all users following the specified company
            query = select(User.id).join(
                Follow, User.id == Follow.user_id).where(
                    Follow.stock_ticker == ticker)
            result = db.session.execute(query)

            if result:
                for row in result:
                    # Send a notification to the current user
                    query = insert(Notification).values(
                        user_id=row[0],
                        message=f"New articles available for {ticker}!")
                    db.session.execute(query)
                    notification = Notification.query.order_by(Notification.id.desc()).first()
                    socketio.emit('notification', {'id': notification.id, 'message': notification.message, 'time': notification.time.strftime('%Y-%m-%d %H:%M:%S')}, room=str(row[0]))

    def backlog(self):
        """
        Retrieves and updates the companies' data for the past 7 days.

        This method retrieves a list of dates from yesterday to 8 days ago and
        updates the companies' data for each date in the list.

        Returns:
            None
        """
        # Get a list of dates from yesterday to 8 days ago
        dates = [date.today() - timedelta(days=i) for i in range(1, 8)]

        # Update companies for each date in the list
        for d in dates:
            print(d)
            self.update_companies(date=d)
