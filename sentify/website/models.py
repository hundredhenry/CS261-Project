from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date
from . import db

# Model of a user
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    verified = db.Column(db.Boolean(), default = False) 
    firstname = db.Column(db.String(15), nullable = False)
    email = db.Column(db.String(30), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)

    # Relations
    notifications = db.relationship('Notification', backref = 'user_notif')
    follows = db.relationship('Follow', backref = 'user_follow')

    def __init__(self, firstname, email, password_hash):
        self.firstname = firstname
        self.email = email
        self.password_hash = password_hash

# Model of a notification
class Notification(UserMixin, db.Model):
    __tablename__ = 'notifications'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    read = db.Column(db.Integer, default = False)
    message = db.Column(db.Text, nullable = False)

    def __init__(self, userID, message):
        self.userID = userID
        self.message = message
        
# Model of a follow
class Follow(UserMixin, db.Model):
    __tablename__ = 'follows'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    stock_ticker = db.Column(db.String(10), db.ForeignKey('companies.stock_ticker'), nullable = False)

    def __init__(self, userID, stock_ticker):
        self.userID = userID
        self.stock_ticker = stock_ticker
        
# Model of a company
class Company(UserMixin, db.Model):
    __tablename__ = 'companies'

    # Attributes
    stock_ticker = db.Column(db.String(10), primary_key = True)
    company_name = db.Column(db.String(20), nullable = False)
    sector_name = db.Column(db.String(20), nullable = False)

    # Relations
    articles = db.relationship('Article', backref = 'company_article')
    follows = db.relationship('Follow', backref = 'company_follow')

    def __init__(self, stock_ticker, company_name, sector_name):
        self.stock_ticker = stock_ticker
        self.company_name = company_name
        self.sector_name = sector_name
        
# Model of an article
class Article(UserMixin, db.Model):
    __tablename__ = 'articles'

    # Attributes
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(100), nullable = False)
    stock_ticker = db.Column(db.String(10), db.ForeignKey('companies.stock_ticker'), nullable = False)
    source_name = db.Column(db.String(20), nullable = False)
    source_domain = db.Column(db.String(20), nullable = False)
    url = db.Column(db.String(100), nullable = False)
    published = db.Column(db.Date, nullable = False)
    description = db.Column(db.Text)
    banner_image = db.Column(db.String(100))
    sentiment_label = db.Column(db.String(10), nullable = False)
    sentiment_score = db.Column(db.Float, nullable = False)

    def __init__(self, title, stock_ticker, source_name, source_domain, url, published, description, banner_image, 
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

# Add data to the database
def dbinit():
    # Add companies alphabetically by stock ticker
    company_list = [
        Company("AAPL", "Apple Inc.", "Technology")   
    ]
    db.session.add_all(company_list)

    # Commit changes to the database
    db.session.commit()