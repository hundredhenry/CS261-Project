import re
import random

from urllib.parse import urlparse
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
from flask_socketio import join_room
from recommend import recommend_specific
from sqlalchemy import func, desc

from . import db, socketio
from .models import User, Company, Follow, SentimentRating, Article, Notification
from .token import generate_confirmation_token, confirm_token
from .email import send_email

views = Blueprint("views", __name__)

@socketio.on('join')
def on_join(data):
    room = str(data['room'])
    join_room(room)
    query = db.session.query(Notification).filter(
        Notification.user_id == data['room'],
        not Notification.sent
    ).all()
    for notif in query:
        socketio.emit('notif', {'message': notif.message}, room=room)
        notif.sent = True
    db.session.commit()

@views.route('/')
def landing():
    return render_template('landing_page.html')

@views.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("views.landing"))
    if request.method == "POST":                
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error_occurred = False
        # check if the user is already registered 
        if len(name) < 1:
            flash("Name is too short!", category="name_error")
            error_occurred = True
        if len(email) < 1:
            flash("Email is too short!", category="email_error")
            error_occurred = True
        if not re.match("^[a-zA-Z]*$", name):
            flash('Name must contain only letters!', category='name_error')
            error_occurred = True
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,}$)", email):
            flash('Invalid email address!', category='email_error')
            error_occurred = True
        if password != confirm_password:
            flash('Passwords do not match!', category='pw_match_error')
            error_occurred = True
        if len(password) < 8:
            flash('Password must be at least 8 characters!', category='pw_error')
            error_occurred = True
        if not error_occurred:
            try:
                user_exists  = User.query.filter_by(email=email).first()
            except SQLAlchemyError:
                abort(500,
                "Unable to continue with registration.Please return to homepage and try again.")
            if user_exists:
                flash("This email is already registered!", category="email_error")
                return redirect(url_for("views.register"))
            new_user = User(firstname=name, email=email,
                            password_hash=generate_password_hash(password))
            # add this user to the DB
            # begin user verification via email check
            # do email sending process here
            token = generate_confirmation_token(email)
            confirm_url = url_for('views.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email - Sentify"
            new_user.confirmation_token = token
            db.session.add(new_user)
            db.session.commit()

            send_email(subject, email, html)
            session.clear()
            return redirect(url_for("views.unconfirmed"))

    return render_template('register.html')

@views.route('/unconfirmed/')
def unconfirmed():
    return render_template('unconfirmed.html')

@views.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if email is None:
        abort(400, 'The confirmation link is invalid or has expired.')
    user = User.query.filter_by(email=email).first()

    if user:
        if user.verified:
            flash('Account already confirmed. Please login.', category='info')
            return redirect(url_for("views.login"))
        if user.confirmation_token != token:
            abort(400, "The confirmation link is outdated")
        else:
            user.verified = True
            db.session.commit()
            flash('Account confirmed - Please login.', category='success')
        return redirect(url_for("views.login")) 

@views.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard"))
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        is_remember = 'remember' in request.form
        user = User.query.filter_by(email=email).first()
        if user:
            if not user.verified:
                flash("Please verify your email first!", category="verify_error")
            elif check_password_hash(user.password_hash, password):
                flash("Logged in successfully", category="login_success")
                login_user(user, remember=is_remember)
                session['user_id'] = user.id
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for("views.dashboard")
                return redirect(next_page)
            else:
                flash("Email or password is incorrect!", category="login_error")
        else:
            flash("Email or password is incorrect!", category="login_error")
    return render_template('login.html')

@views.route('/resend/', methods=['GET', 'POST'])
def resend_email():
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard"))
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email, verified=False).first()
        if user:
            token = generate_confirmation_token(email)
            user.confirmation_token = token
            db.session.commit()
            confirm_url = url_for('views.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email - Sentify"

            send_email(subject, email, html)
            return redirect(url_for("views.unconfirmed"))
        flash('This email is not registered or is already verified!', category='email_error')

    return render_template('resend.html')

@views.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.landing"))

def daily_sentiment(stock_ticker):
    # Query to get daily sentiment
    results = db.session.query(
        SentimentRating.date,
        SentimentRating.rating
    ).filter(SentimentRating.stock_ticker == stock_ticker
    ).order_by(SentimentRating.date.asc()).all()

    # Extract dates and ratings from the query results
    labels = [result.date.strftime('%d-%m-%y') for result in results]
    data = [round(result.rating, 2) for result in results]

    # Prepare data for Chart.js
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': f'Daily Sentiment for {stock_ticker}',
            'data': data,
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)',
            'lineTension': 0.1
        }],
    }

    return chart_data

def industry_sentiment(stock_ticker):
    # Query to get the sector ID of the company
    sector_id = db.session.query(Company.sector_id).filter(Company.stock_ticker == stock_ticker).scalar()

    if sector_id is None:
        return None  # Sector ID not found for the given stock ticker

    # Query to get stock tickers of all companies within the same sector
    companies = db.session.query(Company.stock_ticker).filter(Company.sector_id == sector_id).all()

    # Initialize a list to hold the average sentiment ratings for each company
    company_sentiments = []

    # Loop through each company in the sector
    for company in companies:
        stock_ticker = company[0]

        # Query to get the sentiment ratings of the company
        sentiment_ratings = db.session.query(SentimentRating.rating) \
                                      .filter(SentimentRating.stock_ticker == stock_ticker) \
                                      .all()

        # Calculate the average sentiment rating for this company
        if sentiment_ratings:
            average_sentiment = sum(rating[0] for rating in sentiment_ratings) / len(sentiment_ratings)
            company_sentiments.append(average_sentiment)

    # Calculate the overall average sentiment for the sector
    if company_sentiments:
        overall_average_sentiment = round(sum(company_sentiments) / len(company_sentiments))
    else:
        overall_average_sentiment = None

    return overall_average_sentiment


@views.route('/companies/<ticker>')
@login_required
def company(ticker):
    company = Company.query.get(ticker)
    
    if not company:
        abort(404, "Company not found")

    average_rating = db.session.query(func.avg(SentimentRating.rating)).filter_by(stock_ticker=ticker).scalar()
    positive = round(float(average_rating)) if average_rating else 0
    negative = 100 - positive
    total_articles = db.session.query(func.count(Article.id)).filter(Article.stock_ticker == ticker).scalar()
    positive_articles = db.session.query(func.count(Article.id)).filter(Article.stock_ticker == ticker, Article.sentiment_label == 'Positive').scalar()
    negative_articles = total_articles - positive_articles
    industry_average = industry_sentiment(ticker)
    chart_data = daily_sentiment(ticker)
    is_following = Follow.query.filter_by(user_id=current_user.id, stock_ticker=ticker).first()
    return render_template('base_company.html',
                           ticker=ticker,
                           desc=company.description,
                           sector=company.sector_company.sector_name,
                           positive = positive,
                           negative = negative,
                           total_articles = total_articles,
                           positive_articles = positive_articles,
                           negative_articles = negative_articles,
                           industry_average = industry_average,
                           chart_data = chart_data,
                           is_following = is_following is not None)

def random_color():
    return '#' + ''.join(random.choices('0123456789abcdef', k=6))

def get_following():
    if current_user.is_authenticated:
        following = Follow.query.filter_by(user_id=current_user.id).all()
        return [follow.stock_ticker for follow in following]
    return []

def get_companies():
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            companies = Company.query.with_entities(
                Company.stock_ticker, Company.company_name).order_by(
                Company.company_name).all()
            results = [{'stock_ticker': company.stock_ticker, 'company_name': company.company_name}
                       for company in companies]
            return results
        except SQLAlchemyError:
            attempts += 1
            if attempts == max_attempts:
                raise

@views.route('/companies/search/')
@login_required
def search_companies():
    followed_companies = get_following()
    suggested_companies = [company.stock_ticker for company in recommend_specific(current_user.id)]
    return render_template('company_search.html',
                           companies=followed_companies,
                           suggested_companies=suggested_companies,
                           randomColor=random_color,
                           showNavSearchBar=False)

@views.route('/dashboard')
def dashboard():
    followed_companies = get_following()
    suggested_companies = [company.stock_ticker for company in recommend_specific(current_user.id)]
    return render_template('dashboard.html',
                           companies=followed_companies,
                           suggested_companies=suggested_companies,
                           randomColor=random_color)

@views.route('/companies/')
@login_required
def all_companies():
    companies = get_companies()
    following = get_following()
    return render_template('all_companies.html', companies=companies, following=following)
      
@views.route('/api/modify/follow', methods=['POST'])
@login_required
def modify_follow():
    data = request.get_json()
    ticker = data.get('ticker')
    if not ticker:
        return jsonify({'error': 'No ticker provided'}), 400
    company_exists = Company.query.filter_by(stock_ticker=ticker).first()
    if not company_exists:
        return jsonify({'error': 'Ticker does not exist'}), 404

    is_following = Follow.query.filter_by(user_id=current_user.id, stock_ticker=ticker).first()
    if is_following:
        db.session.delete(is_following)
        db.session.commit()
        return jsonify({'status': 'unfollowed', 'ticker': ticker})

    new_follow = Follow(user_id=current_user.id, stock_ticker=ticker)
    db.session.add(new_follow)
    db.session.commit()
    return jsonify({'status': 'followed', 'ticker': ticker})

@views.route('/api/get/companies', methods=['GET'])
def retrieve_companies():
    try:
        results = get_companies()
        return jsonify(results)
    except SQLAlchemyError:
        return jsonify({'error': 'Maximum number of attempts reached.'}), 500

@views.route('/api/get/articles', methods=['GET'])
@login_required
def company_articles():
    tickers = request.args.get('tickers')
    
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    tickers = set(tickers.split(','))

    articles_json = {}
    for ticker in tickers:
        company = Company.query.get(ticker)
        if not company:
            articles_json[ticker] = {'error': f'{ticker} does not exist'}
            continue
        
        articles_json[ticker] = [
            {
                "url": article.url,
                "title": article.title,
                "source": article.source_name,
                "source_domain": article.source_domain,
                "published": article.published.strftime('%Y-%m-%d'),
                "description": article.description,
                "banner_image": article.banner_image,
                "sentiment_label": article.sentiment_label,
                "sentiment_score": article.sentiment_score,
                "topics": [topic.topic for topic in article.topics]
            }
            for article in company.articles
        ]
    return jsonify({'articles': articles_json})

@views.route('/api/get/notifications', methods=['GET'])
@login_required
def get_notifs():
    notifications = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).order_by(desc(Notification.time)).all()
    notif_list = [{"message": notif.message,
                   "time": notif.time.strftime('%Y-%m-%d %H:%M:%S')}
                  for notif in notifications]
    
    return jsonify(notif_list)
    
@views.route('/api/test/notifs', methods=['GET'])
def add_notifs():
    test_notifications = [
        Notification(1, "Test notification 1", False),
        Notification(1, "Test notification 2", False),
        Notification(1, "Test notification 3", False),
        Notification(1, "Test notification 4", False),
        Notification(1, "Test notification 5", False),
        Notification(1, "Test notification 6", False),
        Notification(1, "Test notification 7", False),
        Notification(1, "Test notification 8", False),
        Notification(1, "Test notification 9", False),
        Notification(1, "Test notification 10", False)
    ]
    db.session.add_all(test_notifications)
    db.session.commit()
    return jsonify({'status': 'success'})