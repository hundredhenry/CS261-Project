import unittest
from sentify.website import create_app, db
from sentify.website.models import User, Notification, Follow, Sector, Company, Article
from sentify.website.recommend import recommend_specific
from tests.test_config import TestConfig
from datetime import date, datetime

class AuthBase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = db
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()

    def addEntry(self, entry):
        self.db.session.add(entry)
        self.db.session.commit()

    test_strings = [-1, 1, 0.5, '', True, date.today()]
    test_integers = [-1, 0.5, 'a', True, date.today()]
    test_dates = [-1, 1, 0.5, 'a', True]
    test_texts = [-1, 1, 0.5, True, date.today()]
    test_floats = ['a', True, date.today()]

# Insert tests for the user table
class UserTest(AuthBase):
    # Setup user test cases
    valid_firstname = 'testname'
    valid_email = 'test@email.com'
    valid_password_hash = 'passwordhash'
    valid_confirmation_token = 'Test Token'
    strings = AuthBase.test_strings.copy()

    user_tests = [
        ('Valid User', valid_firstname, valid_email, valid_password_hash, valid_confirmation_token, True),
        ('Invalid First Name', strings + ['a'*17], valid_email, valid_password_hash, valid_confirmation_token, False),
        ('Invalid Email', valid_firstname, strings + ['a'*49], valid_password_hash, valid_confirmation_token, False),
        ('Invalid Password Hash', valid_firstname, valid_email, strings + ['a'*257], valid_confirmation_token, False),
        ('Invalid Confirmation Token', valid_firstname, valid_email, valid_password_hash, strings, False)
    ]

    # Run user test cases
    def test_insert_user(self):
        for _, firstname, email, password_hash, con_token, valid in self.user_tests:
            with self.subTest(msg=_):
                user = User(firstname, email, password_hash, con_token)
                self.addEntry(user)
                result = User.query.filter_by(firstname=firstname, email=email, password_hash=password_hash, confirmation_token=con_token).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.firstname, firstname)
                else:
                    self.assertIsNone(result)

# Insert tests for the notification table
# Add time attribute (type datetime)
class NotificationTest(AuthBase):
    # Setup notification test cases
    valid_user_id = 1
    valid_message = 'Test message'
    messages = AuthBase.test_strings.copy()
    user_ids = AuthBase.test_integers.copy()

    notification_tests = [
        ('Valid notification', valid_user_id, valid_message, True),
        ('Invalid userid', user_ids, valid_message, False),
        ('Invalid message', valid_user_id, messages, False)
    ]

    # Run notification test cases
    def test_insert_notification(self):
        for _, user_id, message, valid in self.notification_tests:
            with self.subTest(msg=_):
                notification = Notification(user_id, message)
                self.addEntry(notification)
                result = Notification.query.filter_by(user_id=user_id, message=message).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.message, message)
                else:
                    self.assertIsNone(result)

# Insert tests for the follow table
class FollowTest(AuthBase):
    # Setup follow test cases
    valid_userid = 1
    valid_stock_ticker = 'TEST'
    stock_tickers = AuthBase.test_strings.copy()
    user_ids = AuthBase.test_integers.copy()

    follow_tests = [
        ('Valid follow', valid_userid, valid_stock_ticker, True),
        ('Invalid user_id', user_ids, valid_stock_ticker, False),
        ('Invalid stock_ticker', valid_userid, stock_tickers, False)
    ]

    # Run follow test cases
    def test_insert_follow(self):
        for _, user_id, stock_ticker, valid in self.follow_tests:
            with self.subTest(msg=_):
                follow = Follow(user_id, stock_ticker)
                self.addEntry(follow)
                result = Follow.query.filter_by(user_id=user_id, follow=follow).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.user_id, user_id)
                else:
                    self.assertIsNone(result)

# Insert tests for the sector table
class SectorTest(AuthBase):
    # Setup sector test cases
    valid_sector_name = 'Test Sector'
    sectors = AuthBase.test_strings.copy()

    sector_tests = [
        ('Valid sector', valid_sector_name, True),
        ('Invalid sector', sectors, False)
    ]

    # Run sector test cases
    def test_insert_sector(self):
        for _, sector_name, valid in self.sector_tests:
            with self.subTest(msg=_):
                sector = Sector(sector_name)
                self.addEntry(sector)
                result = Follow.query.filter_by(sector_name=sector_name).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.sector_name, sector_name)
                else:
                    self.assertIsNone(result)

# Insert tests for the company table
class CompanyTest(AuthBase):
    # Setup company test cases
    valid_stock_ticker = 'TEST'
    valid_company_name = 'Test Company'
    valid_sector_id = 1
    valid_description = 'Test Description'
    valid_updated = date.today()
    strings = AuthBase.test_strings.copy()
    sector_ids = AuthBase.test_integers.copy()
    dates = AuthBase.test_dates.copy()

    company_tests = [
        ('Valid company', valid_stock_ticker, valid_company_name, valid_sector_id, valid_description, valid_updated, True),
        ('Invalid stock_ticker', strings, valid_company_name, valid_sector_id, valid_description, valid_updated, False),
        ('Invalid company_name', valid_stock_ticker, strings, valid_sector_id, valid_description, valid_updated, False),
        ('Invalid sector_id', valid_stock_ticker, valid_company_name, sector_ids, valid_description, valid_updated, False),
        ('Invalid description', valid_stock_ticker, valid_company_name, valid_sector_id, strings, valid_updated, False),
        ('Invalid rating', valid_stock_ticker, valid_company_name, valid_sector_id, valid_description, valid_updated, False),
        ('Invalid updated', valid_stock_ticker, valid_company_name, valid_sector_id, valid_description, dates, False),
    ]

    # Run company test cases
    def test_insert_company(self):
        for _, stock_ticker, company_name, sector_id, description, updated, valid in self.sector_tests:
            with self.subTest(msg=_):
                company = Company(stock_ticker, company_name, sector_id, description, updated)
                self.addEntry(company)
                result = Company.query.filter_by(company_name=company_name).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.company_name, company_name)
                else:
                    self.assertIsNone(result)

# Insert tests for the article table
class ArticleTest(AuthBase):
    # Setup article test cases
    valid_url = 'Test URL'
    valid_title = 'Test Title'
    valid_stock_ticker = 'TEST'
    valid_source = 'Test Source'
    valid_domain = 'Test Domain'
    valid_date = date.today()
    valid_description = 'Test Description'
    valid_image = 'Test Image'
    valid_label = 'Test Label'
    valid_score = 1
    strings = AuthBase.test_strings.copy()
    dates = AuthBase.test_dates.copy()
    scores = AuthBase.test_floats.copy()

    article_tests = [
        ('Valid article', valid_title, valid_stock_ticker, valid_source, valid_domain, valid_url, valid_date, valid_description, valid_image, valid_label, valid_score, True),
        ('Invalid title', strings, valid_stock_ticker, valid_source, valid_domain, valid_url, valid_date, valid_description, valid_image, valid_label, valid_score, False),
        ('Invalid stock_ticker', valid_title, strings, valid_source, valid_domain, valid_url, valid_date, valid_description, valid_image, valid_label, valid_score, False),
        ('Invalid source_name', valid_title, valid_stock_ticker, strings, valid_domain, valid_url, valid_date, valid_description, valid_image, valid_label, valid_score, False),
        ('Invalid source_domain', valid_title, valid_stock_ticker, valid_source, strings, valid_url, valid_date, valid_description, valid_image, valid_label, valid_score, False),
        ('Invalid url', valid_title, valid_stock_ticker, valid_source, valid_domain, strings, valid_date, valid_description, valid_image, valid_label, valid_score, False),
        ('Invalid published', valid_title, valid_stock_ticker, valid_source, valid_domain, valid_url, dates, valid_description, valid_image, valid_label, valid_score, False),
        ('Invalid description', valid_title, valid_stock_ticker, valid_source, valid_domain, valid_url, valid_date, strings, valid_image, valid_label, valid_score, False),
        ('Invalid banner_image', valid_title, valid_stock_ticker, valid_source, valid_domain, valid_url, valid_date, valid_description, strings, valid_label, valid_score, False),
        ('Invalid sentiment_label', valid_title, valid_stock_ticker, valid_source, valid_domain, valid_url, valid_date, valid_description, valid_image, strings, valid_score, False),
        ('Invalid sentiment_score', valid_title, valid_stock_ticker, valid_source, valid_domain, valid_url, valid_date, valid_description, valid_image, valid_label, scores, False)
    ]

    # Run article test cases
    def test_insert_article(self):
        for _, title, stock_ticker, source_name, source_domain, url, published, description, image, label, score, valid in self.sector_tests:
            with self.subTest(msg=_):
                article = Article(title, stock_ticker, source_name, source_domain, url, published, description, image, label, score)
                self.addEntry(article)
                result = Article.query.filter_by(title=title).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.title, title)
                else:
                    self.assertIsNone(result)

# Insert tests for the topic table
class TopicTest(AuthBase):
    # Setup topic test cases
    valid_topic = 'Test Topic'
    topics = AuthBase.test_strings.copy()
    topic_tests = [
        ('Valid topic', valid_topic, True),
        ('Invalid topic_name', topics, False)
    ]

    # Run company test cases
    def test_insert_company(self):
        for _, stock_ticker, company_name, sector_id, description, updated, valid in self.topic_tests:
            with self.subTest(msg=_):
                company = Company(stock_ticker, company_name, sector_id, description, updated)
                self.addEntry(company)
                result = Company.query.filter_by(company_name=company_name).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.company_name, company_name)
                else:
                    self.assertIsNone(result)

# Insert tests for the article-topic table
class ArticleTopicTest(AuthBase):
    # Setup article-topic test cases
    valid_id = 1

    # Run company test cases
    def test_insert_company(self):
        for _, stock_ticker, company_name, sector_id, description, updated, valid in self.sector_tests:
            with self.subTest(msg=_):
                company = Company(stock_ticker, company_name, sector_id, description, updated)
                self.addEntry(company)
                result = Company.query.filter_by(company_name=company_name).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.company_name, company_name)
                else:
                    self.assertIsNone(result)

# Insert tests for the sentiment rating table
class SentimentRating(AuthBase):
    # Setup sentiment rating tests cases
    valid_stock_ticker = 'TEST'
    valid_date = date.today()
    valid_rating = 1
    sentiment_tests = []

    # Run sentiment rating test cases
    def test_insert_sentiment(self):
        for _, stock_ticker, date, rating, valid in self.sentiment_tests:
            with self.subTest(msg=_):
                company = SentimentRating(stock_ticker, date, rating)
                self.addEntry(company)
                result = SentimentRating.query.filter_by(stock_ticker=stock_ticker).first()

                if valid:
                    self.assertIsNotNone(result)
                    self.assertEqual(result.stock_ticker, stock_ticker)
                else:
                    self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()