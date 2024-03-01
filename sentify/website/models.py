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
    sectorID = db.Column(db.Integer, db.ForeignKey('sectors.id'), nullable = False)
    description = db.Column(db.Text)

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
    url = db.Column(db.String(100), primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    stock_ticker = db.Column(db.String(10), db.ForeignKey('companies.stock_ticker'), nullable = False)
    source_name = db.Column(db.String(20), nullable = False)
    source_domain = db.Column(db.String(20), nullable = False)
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
    entertainmentID = Sector.query.filter_by(sector_name = "Entertainment").first().id
    financeID = Sector.query.filter_by(sector_name = "Finance").first().id
    foodbevID = Sector.query.filter_by(sector_name = "Food and Beverage").first().id
    healthcareID = Sector.query.filter_by(sector_name = "Healthcare").first().id
    manufacturingID = Sector.query.filter_by(sector_name = "Manufacturing").first().id
    retailID = Sector.query.filter_by(sector_name = "Retail").first().id
    techID = Sector.query.filter_by(sector_name = "Technology").first().id

    # Add companies alphabetically by stock ticker
    company_list = [
        Company("AAPL", "Apple", techID),
        Company("AMZN", "Amazon.com", techID),
        Company("COST", "Costco Wholesale", retailID),
        Company("GOOGL", "Alphabet", techID),
        Company("HD", "The Home Depot", retailID),
        Company("JNJ", "Johnson & Johnson", healthcareID),
        Company("JPM", "JPMorgan Chase", financeID),
        Company("KO", "Coca-Cola", foodbevID),
        Company("LLY", "Eli Lilly and Company", healthcareID),
        Company("MA", "Mastercard", financeID),
        Company("MCD", "McDonald's", foodbevID),
        Company("MSFT", "Microsoft", techID),
        Company("NFLX", "Netflix", entertainmentID),
        Company("NVDA", "NVIDIA", techID),
        Company("NVO", "Novo Nordisk A/S", healthcareID),
        Company("PEP", "PepsiCo", foodbevID),
        Company("PG", "Proctor & Gamble", manufacturingID),
        Company("TM", "Toyota Motors", manufacturingID),
        Company("V", "Visa", financeID),
        Company("WMT", "Walmart", retailID)   
    ]
    db.session.add_all(company_list)

    # Commit changes to the database
    db.session.commit()