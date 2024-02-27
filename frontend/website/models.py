from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date
from . import db

# Model of a user
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Attributes
    id = db.Column(db.Integer, primary_key = True)
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
    id = db.Column(db.Integer, primary_key = True)
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
    id = db.Column(db.Integer, primary_key = True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    stock_ticker = db.Column(db.String(10), db.ForeignKey('companies.stock_ticker'), nullable = False)

    def __init__(self, userID, stock_ticker):
        self.userID = userID
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
        
# Model of a source
class Source(UserMixin, db.Model):
    __tablename__ = 'sources'

    # Attributes
    id = db.Column(db.Integer, primary_key = True)
    source_name = db.Column(db.String(20), nullable = False)

    # Relation
    articles = db.relationship('Article', backref = 'source_article')

    def __init__(self, source_name):
        self.source_name = source_name
        
# Model of a company
class Company(UserMixin, db.Model):
    __tablename__ = 'companies'

    # Attributes
    stock_ticker = db.Column(db.String(10), primary_key = True)
    company_name = db.Column(db.String(20), nullable = False)
    sectorID = db.Column(db.Integer, db.ForeignKey('sectors.id'), nullable = False)

    # Relations
    articles = db.relationship('Article', backref = 'company_article')
    follows = db.relationship('Follow', backref = 'company_follow')

    def __init__(self, stock_ticker, company_name, sectorID):
        self.stock_ticker = stock_ticker
        self.company_name = company_name
        self.sectorID = sectorID
        
# Model of an article
class Article(UserMixin, db.Model):
    __tablename__ = 'articles'

    # Attributes
    id = db.Column(db.Integer, primary_key = True)
    sourceID = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable = False)
    stock_ticker = db.Column(db.String(10), db.ForeignKey('companies.stock_ticker'), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    probability = db.Column(db.Float, nullable = False)
    link = db.Column(db.String(100), nullable = False)
    summary = db.Column(db.Text)
    published = db.Column(db.Date, nullable = False)

    def __init__(self, sourceID, stock_ticker, rating, probability, link, summary):
        self.sourceID = sourceID
        self.stock_ticker = stock_ticker
        self.rating = rating
        self.probability = probability
        self.link = link
        self.summary = summary
        self.published = date.today()

# Add data to the database
def  dbinit():

    # Add sectors in alphabetical order
    sector_list = [
        Sector("Entertainment"),
        Sector("Healthcare"),
        Sector("Finance"),
        Sector("Food and Beverage"),
        Sector("Manufacturing"),
        Sector("Retail"),
        Sector("Technology")
    ]
    db.session.add_all(sector_list)

    # Add companies alphabetically by stock ticker
    company_list = [
        Company("AAPL", "Apple Inc.", 6),
        Company("AMZN", "Amazon.com, Inc.", 6),
        Company("COST", "Costco Wholesale Corporation", 5),
        Company("GOOGL", "Alphabet Inc.", 6),
        Company("HD", "The Home Depot, Inc.", 5),
        Company("JNJ", "Johnson & Johnson", 1),
        Company("JPM", "JP Morgan Chase & Co.", 2),
        Company("KO", "The Coca-Cola Company", 3),    
        Company("LLY", "Eli Lilly and Company", 1),
        Company("MA", "Mastercard Incorporated", 2),
        Company("MCD", "McDonald's Corporation", 3),
        Company("MSFT", "Microsoft Corporation", 6),
        Company("NFLX", "Netflix, Inc.", 0),
        Company("NVDA", "NVIDIA Corporation", 6),
        Company("NVO", "Novo Nordisk A/S", 1),
        Company("PEP", "PepsiCo, Inc.", 3),
        Company("PG", "The Procter & Gamble", 4),
        Company("TM", "Toyota Motor Corporation", 4),
        Company("V", "Visa Inc.", 2),
        Company("WMT", "Walmart Inc.", 5),   
    ]
    db.session.add_all(company_list)

    # Commit changes to the database
    db.session.commit()