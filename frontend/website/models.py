from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db

# Model of a user
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    verified = db.Column(db.Boolean(), nullable=False, default=False) 
    firstname = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, firstname, email, password_hash):
        self.firstname = firstname
        self.email = email
        self.password_hash = password_hash

# Model of a notification
class Notification(UserMixin, db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key = True)
    userID = db.Column(db.Integer, nullable = False) # Foreign key
    read = db.Column(db.Integer, nullable = False) # Default: 0 - 1 for read, 0 for unread
    message = db.Column(db.Text, nullable = False)

    def __init__(self, userID, read, message):
        self.userID = userID
        self.read = read
        self.message = message
        
# Model of a follow
class Follow(UserMixin, db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key = True)
    userID = db.Column(db.Integer, nullable = False) # Foreign key
    stock_ticker = db.Column(db.String(10), nullable = False) # Foreign key

    def __init__(self, userID, stock_ticker):
        self.userID = userID
        self.stock_ticker = stock_ticker
        
# Model of a sector
class Sector(UserMixin, db.Model):
    __tablename__ = 'sectors'
    id = db.Column(db.Integer, primary_key = True)
    sector_name = db.Column(db.String(20), nullable = False)

    def __init__(self, sector_name):
        self.sector_name = sector_name
        
# Model of a source
class Source(UserMixin, db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, primary_key = True)
    source_name = db.Column(db.Integer, nullable = False)

    def __init__(self, source_name):
        self.source_name = source_name
        
# Model of a company
class Company(UserMixin, db.Model):
    __tablename__ = 'companies'
    stock_ticker = db.Column(db.String(10), primary_key = True)
    company_name = db.Column(db.String(20), nullable = False)
    sectorID = db.Column(db.Integer, nullable = False) # Foreign key

    def __init__(self, stock_ticker, company_name, sectorID):
        self.stock_ticker = stock_ticker
        self.company_name = company_name
        self.sectorID = sectorID
        
# Model of an article
class Article(UserMixin, db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key = True)
    sourceID = db.Column(db.Integer, nullable = False) # Foreign key
    stock_ticker = db.Column(db.String(10), nullable = False) # Foreign key
    rating = db.Column(db.Integer, nullable = False)
    probability = db.Column(db.Float, nullable = False)
    link = db.Column(db.String(100), nullable = False)
    summary = db.Column(db.Text)
    published = db.Column(db.Date, nullable = False) # Default: current date

    def __init__(self, sourceID, stock_ticker, rating, probability, link, summary, published):
        self.sourceID = sourceID
        self.stock_ticker = stock_ticker
        self.rating = rating
        self.probability = probability
        self.link = link
        self.summary = summary
        self.published = published
