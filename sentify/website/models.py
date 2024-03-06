from flask_login import UserMixin
from datetime import datetime, date
from . import db

# Model of a user
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    verified = db.Column(db.Boolean(), default = False)
    firstname = db.Column(db.String(16), nullable = False)
    email = db.Column(db.String(48), unique = True, nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    confirmation_token = db.Column(db.Text, nullable = True)

    # Relations
    notifications = db.relationship('Notification', backref = 'user_notif')
    follows = db.relationship('Follow', backref = 'user_follow')

    def __init__(self, firstname, email, password_hash):
        self.firstname = firstname
        self.email = email
        self.password_hash = password_hash
        self.confirmation_token = None

# Model of a notification
class Notification(db.Model):
    __tablename__ = 'notifications'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    read = db.Column(db.Boolean, default = False)
    sent = db.Column(db.Boolean, default = False)
    message = db.Column(db.Text, nullable = False)
    time = db.Column(db.DateTime, default = datetime.now)

    def __init__(self, user_id, message, sent):
        self.user_id = user_id
        self.message = message
        self.sent = sent

# Model of a follow
class Follow(UserMixin, db.Model):
    __tablename__ = 'follows'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    stock_ticker = db.Column(db.String(10),
                             db.ForeignKey('companies.stock_ticker'),
                             nullable = False)

    def __init__(self, user_id, stock_ticker):
        self.user_id = user_id
        self.stock_ticker = stock_ticker

# Model of a sector
class Sector(UserMixin, db.Model):
    __tablename__ = 'sectors'

    # Attributes
    id = db.Column(db.Integer, primary_key = True)
    sector_name = db.Column(db.String(20), nullable = False)

    # Relation
    companies = db.relationship('Company', backref = 'sector_company')

    def __init__(self, sector_name):
        self.sector_name = sector_name

# Model of a company
class Company(UserMixin, db.Model):
    __tablename__ = 'companies'

    # Attributes
    stock_ticker = db.Column(db.String(10), primary_key = True)
    company_name = db.Column(db.String(32), nullable = False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectors.id'), nullable = False)
    description = db.Column(db.Text)
    last_updated = db.Column(db.Date, default = date(1970, 1, 1))

    # Relations
    articles = db.relationship('Article', backref = 'company_article')
    follows = db.relationship('Follow', backref = 'company_follow')

    def __init__(self, stock_ticker, company_name, sector_id):
        self.stock_ticker = stock_ticker
        self.company_name = company_name
        self.sector_id = sector_id

# Model of an article
class Article(UserMixin, db.Model):
    __tablename__ = 'articles'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    url = db.Column(db.Text, nullable = False)
    title = db.Column(db.Text, nullable = False)
    stock_ticker = db.Column(db.String(10),
                             db.ForeignKey('companies.stock_ticker'),
                             nullable = False)
    source_name = db.Column(db.String(50), nullable = False)
    source_domain = db.Column(db.Text, nullable = False)
    published = db.Column(db.Date, nullable = False)
    description = db.Column(db.Text)
    banner_image = db.Column(db.Text)
    sentiment_label = db.Column(db.String(10), nullable = False)
    sentiment_score = db.Column(db.Float, nullable = False)
    topics = db.relationship('Topic', secondary = 'article_topics', backref = 'article_topic')

    def __init__(self, title, stock_ticker, source_name, source_domain,
                 url, published, description, banner_image, 
                 sentiment_label, sentiment_score):
        self.title = title
        self.stock_ticker = stock_ticker
        self.source_name = source_name
        self.source_domain = source_domain
        self.url = url
        self.published = published
        self.description = description
        self.banner_image = banner_image
        self.sentiment_label = sentiment_label
        self.sentiment_score = sentiment_score
        self.topics = []

class Topic(db.Model):
    __tablename__ = 'topics'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    topic = db.Column(db.String(50), nullable = False)

    def __init__(self, topic):
        self.topic = topic

class ArticleTopic(db.Model):
    __tablename__ = 'article_topics'

    # Attributes
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), primary_key = True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), primary_key = True)

    def __init__(self, article_id, topic_id):
        self.article_id = article_id
        self.topic = topic_id

class SentimentRating(db.Model):
    __tablename__ = 'sentiment_ratings'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    stock_ticker = db.Column(db.String(10),
                             db.ForeignKey('companies.stock_ticker'),
                             nullable = False)
    date = db.Column(db.Date, nullable = False)
    rating = db.Column(db.Float, nullable = False)

    def __init__(self, stock_ticker, date, rating):
        self.stock_ticker = stock_ticker
        self.date = date
        self.rating = rating


# Add data to the database
def dbinit():
    # Add sectors alphabetically
    sector_list = [
        Sector("Entertainment"),
        Sector("Finance"),
        Sector("Food and Beverage"),
        Sector("Healthcare"),
        Sector("Manufacturing"),
        Sector("Retail"),
        Sector("Technology")
    ]
    db.session.add_all(sector_list)

    # Get the IDs of the sectors
    entertainment_id = Sector.query.filter_by(sector_name = "Entertainment").first().id
    finance_id = Sector.query.filter_by(sector_name = "Finance").first().id
    foodbev_id = Sector.query.filter_by(sector_name = "Food and Beverage").first().id
    healthcare_id = Sector.query.filter_by(sector_name = "Healthcare").first().id
    manufacturing_id = Sector.query.filter_by(sector_name = "Manufacturing").first().id
    retail_id = Sector.query.filter_by(sector_name = "Retail").first().id
    tech_id = Sector.query.filter_by(sector_name = "Technology").first().id

    # Add companies alphabetically by stock ticker
    company_list = [
        Company("AAPL", "Apple", tech_id),
        Company("AMZN", "Amazon.com", tech_id),
        Company("COST", "Costco Wholesale", retail_id),
        Company("GOOG", "Alphabet", tech_id),
        Company("HD", "The Home Depot", retail_id),
        Company("JNJ", "Johnson & Johnson", healthcare_id),
        Company("BRK-A", "Berkshire Hathaway", finance_id),
        Company("KO", "Coca-Cola", foodbev_id),
        Company("LLY", "Eli Lilly and Company", healthcare_id),
        Company("MA", "Mastercard", finance_id),
        Company("MCD", "McDonald's", foodbev_id),
        Company("MSFT", "Microsoft", tech_id),
        Company("NFLX", "Netflix", entertainment_id),
        Company("NVDA", "NVIDIA", tech_id),
        Company("NVO", "Novo Nordisk A/S", healthcare_id),
        Company("PEP", "PepsiCo", foodbev_id),
        Company("PG", "Proctor & Gamble", manufacturing_id),
        Company("TM", "Toyota Motors", manufacturing_id),
        Company("V", "Visa", finance_id),
        Company("WMT", "Walmart", retail_id)   
    ]
    db.session.add_all(company_list)

    # Add topics
    topics = [Topic("Blockchain"), Topic("Earnings"), Topic("IPO"), Topic("Mergers & Acquisitions"), Topic("Financial Markets"), 
              Topic("Economy - Fiscal"), Topic("Economy - Monetary"), Topic("Economy - Macro"), Topic("Energy & Transportation"),
              Topic("Finance"), Topic("Life Sciences"), Topic("Manufacturing"), Topic("Real Estate & Construction"), 
              Topic("Retail & Wholesale"), Topic("Technology")]
    db.session.add_all(topics)

    db.session.commit()
