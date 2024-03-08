import re
from random import choices
from urllib.parse import urlparse

from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, jsonify, session
)
from flask_login import login_user, login_required, logout_user, current_user
from flask_socketio import join_room
from sqlalchemy import func, desc
from werkzeug.security import generate_password_hash, check_password_hash
from recommend import recommend_specific

from . import db, socketio
from .decorators import handle_sqlalchemy_error, handle_api_sqlalchemy_error
from .email import send_email
from .models import User, Company, Follow, SentimentRating, Article, Notification
from .token import generate_confirmation_token, confirm_token

views = Blueprint("views", __name__)

@socketio.on('join')
def on_join(data):
    """
    Function to handle the 'join' event from the client.

    Parameters:
    - data (dict): A dictionary containing the data sent by the client.

    Returns:
    None
    """
    room = str(data['room'])
    join_room(room)

@views.route('/')
def landing():
    """
    Renders the landing page.

    If the user is authenticated, it redirects to the dashboard.
    Otherwise, it renders the landing_page.html template.

    Returns:
        The rendered template for the home directory.
    """
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard"))
    return render_template('landing_page.html')

@views.route('/register/', methods=['GET', 'POST'])
@handle_sqlalchemy_error('views.register',
                         'Unable to register please try again.')
def register():
    """
    Register a new user.

    If the user is already authenticated, they will be redirected to the dashboard.
    If the request method is POST, the user's registration information will be processed.
    The user's name, email, password, and confirm_password are extracted from the request form.
    Validation checks are performed on the name, email, and password fields.
    If any validation errors occur, flash messages are displayed to the user.
    If no errors occur, the user's information is added to the database and a confirmation email is sent.
    The user is then redirected to the unconfirmed page.

    Returns:
        If the request method is GET, renders the register.html template.
        If the user is already authenticated, redirects to the dashboard.
        If the request method is POST and there are validation errors, redirects to the register page.
        If the request method is POST and the registration is successful, redirects to the unconfirmed page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("views.dashboard"))
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error_occurred = False
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
            user_exists  = User.query.filter_by(email=email).first()
            if user_exists:
                flash("This email is already registered!", category="email_error")
                return redirect(url_for("views.register"))

            new_user = User(firstname=name, email=email,
                            password_hash=generate_password_hash(password))
            token = generate_confirmation_token(email)
            confirm_url = url_for('views.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email - Sentify"
            new_user.confirmation_token = token
    
            db.session.add(new_user)
            db.session.commit()

            send_email(subject, email, html)
            session.clear() # ensures session is clean

            return redirect(url_for("views.unconfirmed"))

    return render_template('register.html')

@views.route('/unconfirmed/')
def unconfirmed():
    """
    Renders the 'unconfirmed.html' template.

    Returns:
        The rendered template.
    """
    return render_template('unconfirmed.html')

@views.route('/confirm/<token>')
@handle_sqlalchemy_error('views.resend_email',
                         'Unable to confirm email please try again.')
def confirm_email(token):
    """
    Confirm the user's email address using the provided token.

    Args:
        token (str): The token used for email confirmation.

    Returns:
        redirect: Redirects the user to the appropriate page based on the confirmation status.
    """
    email = confirm_token(token)
    if email is None:
        flash('The confirmation link is invalid or has expired.', category='error')
        return redirect(url_for('views.resend_email'))

    user = User.query.filter_by(email=email).first()
    if user:
        if user.verified:
            flash('Account already confirmed. Please login.', category='info')
            return redirect(url_for("views.login"))
        if user.confirmation_token != token:
            flash('Linked is outdated. Please check your inbox for a new one.', category='error')
            return redirect(url_for('views.resend_email'))

        user.verified = True
        db.session.commit()
        flash('Account confirmed - Please login.', category='success')
        return redirect(url_for("views.login"))

@views.route('/login/', methods=['GET', 'POST'])
@handle_sqlalchemy_error('views.login',
                         'Unable to login please try again.')
def login():
    """
    Handle the login functionality.

    If the user is already authenticated, redirect them to the dashboard.
    If the request method is POST, attempt to log in the user using the provided email and password.
    If the user is successfully logged in, redirect them to the dashboard.
    If the user is not verified, display a flash message asking them to verify their email.
    If the email or password is incorrect, display a flash message indicating the error.
    If the request method is GET, render the login.html template.

    Returns:
        If the user is already authenticated, redirects to the dashboard.
        If the user is successfully logged in, redirects to the referer or dashboard.
        If the request method is GET, renders the login.html template.
    """
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
@handle_sqlalchemy_error('views.resend_email',
                         'Unable to resend email please try again.')
def resend_email():
    """
    Resends the confirmation email to the user.

    If the user is already authenticated, redirects to the dashboard.
    If the request method is POST, retrieves the email from the form data and checks if the user exists and is not verified.
    If the user exists and is not verified, generates a new confirmation token, updates the user's confirmation token in the database,
    and sends a confirmation email to the user's email address.
    If the user does not exist or is already verified, displays an error message.
    Renders the 'resend.html' template.

    Returns:
        If the email is successfully sent, redirects to the 'unconfirmed' page.
        If the user is already authenticated, redirects to the dashboard.
        If the email is not registered or is already verified, displays an error message and stays on the 'resend.html' page.
    """
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
    """
    Logs out the current user and redirects to the landing page.

    Returns:
        A redirect response to the landing page.
    """
    logout_user()
    return redirect(url_for("views.landing"))

def daily_sentiment(stock_ticker):
    """
    Retrieves the daily sentiment data for a given stock ticker.

    Args:
        stock_ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing the data for Chart.js visualization.
            The dictionary has the following structure:
            {
                'labels': [list of dates],
                'datasets': [{
                    'label': 'Daily Sentiment for [stock_ticker]',
                    'data': [list of sentiment ratings],
                    'fill': False,
                    'borderColor': 'rgb(75, 192, 192)',
                    'lineTension': 0.1
                }]
            }
    """
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
    """
    Calculate the overall average sentiment for a given stock ticker within its sector.

    Args:
        stock_ticker (str): The stock ticker symbol of the company.

    Returns:
        float or None: The overall average sentiment rating for the sector, rounded to the nearest integer.
            Returns None if the sector ID is not found or if there are no sentiment ratings for the companies in the sector.
    """
    # Query to get the sector ID of the company
    sector_id = db.session.query(
        Company.sector_id).filter(
        Company.stock_ticker == stock_ticker).scalar()

    if sector_id is None:
        return None

    # Query to get stock tickers of all companies within the same sector
    companies = db.session.query(
        Company.stock_ticker).filter(
        Company.sector_id == sector_id).all()

    # Initialize a list to hold the average sentiment ratings for each company
    company_sentiments = []

    for company in companies:
        stock_ticker = company[0]

        # Query to get the sentiment ratings of the company
        sentiment_ratings = db.session.query(
            SentimentRating.rating).filter(
            SentimentRating.stock_ticker == stock_ticker).all()

        # Calculate the average sentiment rating for this company
        if sentiment_ratings:
            average_sentiment = sum(
                rating[0] for rating in sentiment_ratings
                ) / len(sentiment_ratings)
            company_sentiments.append(average_sentiment)

    # Calculate the overall average sentiment for the sector
    if company_sentiments:
        overall_average_sentiment = round(sum(company_sentiments) / len(company_sentiments))
    else:
        overall_average_sentiment = None

    return overall_average_sentiment


@views.route('/companies/<ticker>')
@login_required
@handle_sqlalchemy_error('views.dashboard',
                         'Error generating company page.')
def company(ticker):
    """
    Renders the company page for the given ticker.

    Args:
        ticker (str): The ticker symbol of the company.

    Returns:
        flask.Response: The rendered company page.
    """
    company = Company.query.get(ticker)

    if not company:
        flash('Company not found!', category='error')
        return redirect(url_for('views.dashboard'))

    average_rating = db.session.query(
        func.avg(
            SentimentRating.rating)).filter_by(
                stock_ticker=ticker).scalar()
    positive = round(float(average_rating)) if average_rating else 0
    negative = 100 - positive
    total_articles = db.session.query(
        func.count(
            Article.id)).filter(
            Article.stock_ticker == ticker).scalar()
    positive_articles = db.session.query(
        func.count(
            Article.id)).filter(
                Article.stock_ticker == ticker,
                Article.sentiment_label == 'Positive').scalar()
    industry_average = industry_sentiment(ticker)
    chart_data = daily_sentiment(ticker)
    is_following = Follow.query.filter_by(
        user_id=current_user.id,
        stock_ticker=ticker).first()
    
    return render_template('base_company.html',
                           ticker=ticker,
                           desc=company.description,
                           sector=company.sector_company.sector_name,
                           positive = positive,
                           negative = negative,
                           total_articles = total_articles,
                           positive_articles = positive_articles,
                           negative_articles = total_articles - positive_articles,
                           industry_average = industry_average,
                           chart_data = chart_data,
                           is_following = is_following is not None)

def random_color():
    """
    Generates a random color in hexadecimal format.

    Returns:
        str: A random color in the format '#RRGGBB'.
    """
    return '#' + ''.join(choices('0123456789abcdef', k=6))


def get_following():
    """
    Retrieves the list of stock tickers that the current user is following.

    Returns:
        A list of stock tickers that the current user is following.
        If the user is not authenticated, an empty list is returned.
    """
    if current_user.is_authenticated:
        following = Follow.query.filter_by(user_id=current_user.id).all()
        return [follow.stock_ticker for follow in following]
    return []

def get_companies():
    """
    Retrieves a list of companies from the database.

    Returns:
        A list of dictionaries containing the stock ticker and company name of each company.
    """
    companies = Company.query.with_entities(
        Company.stock_ticker, Company.company_name).order_by(
        Company.company_name).all()
    results = [{'stock_ticker': company.stock_ticker, 'company_name': company.company_name}
                for company in companies]
    return results

@views.route('/companies/search/')
@login_required
@handle_sqlalchemy_error('views.search_companies',
                        'Error retrieving companies.')
def search_companies():
    """
    Renders the company search page with the following data:
    - followed_companies: a list of companies that the current user is following
    - suggested_companies: a list of recommended companies for the current user
    - randomColor: a function that generates a random color
    - showNavSearchBar: a boolean indicating whether to show the navigation search bar
    
    Returns:
    - The rendered company search template with the above data
    """
    followed_companies = get_following()
    suggested_companies = [company.stock_ticker for company in recommend_specific(current_user.id)]
    return render_template('company_search.html',
                           companies=followed_companies,
                           suggested_companies=suggested_companies,
                           randomColor=random_color,
                           showNavSearchBar=False)

@views.route('/dashboard/')
@login_required
@handle_sqlalchemy_error('views.dashboard',
                        'Error retrieving dashboard data.')
def dashboard():
    """
    Renders the dashboard page with the user's followed companies and suggested companies.

    Returns:
        A rendered template of the dashboard.html page with the following variables:
        - companies: A list of the user's followed companies.
        - suggested_companies: A list of suggested companies based on the user's preferences.
        - randomColor: A random color for the dashboard page.
    """
    followed_companies = get_following()
    suggested_companies = [company.stock_ticker for company in recommend_specific(current_user.id)]
    return render_template('dashboard.html',
                           companies=followed_companies,
                           suggested_companies=suggested_companies,
                           randomColor=random_color)

@views.route('/companies/')
@login_required
@handle_sqlalchemy_error('views.dashboard',
                         'Error loading all companies.')
def all_companies():
    """
    Renders the 'all_companies.html' template with all companies and the user's following status.

    Returns:
        A rendered template with the following variables:
        - companies: A list of companies.
        - following: A list of companies that the user is following.
    """
    companies = get_companies()
    following = get_following()
    return render_template('all_companies.html',
                           companies=companies,
                           following=following)

@views.route('/api/modify/follow', methods=['POST'])
@login_required
@handle_api_sqlalchemy_error('Error modifying follow status.')
def modify_follow():
    """
    Modify the follow status of a user for a given stock ticker.

    Returns:
        A JSON response containing the status of the follow operation and the ticker.

    Raises:
        400: If no ticker is provided in the request.
        404: If the provided ticker does not exist in the database.
    """
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
@login_required
@handle_api_sqlalchemy_error('Error retrieving companies.')
def retrieve_companies():
    """
    Retrieves a list of companies.

    Returns:
        A JSON response containing the list of companies.
    """
    results = get_companies()
    return jsonify(results)

@views.route('/api/get/articles', methods=['GET'])
@login_required
@handle_api_sqlalchemy_error('Error retrieving articles.')
def company_articles():
    """
    Retrieves articles for specified tickers.

    Returns:
        JSON response containing articles for each ticker.

    Raises:
        400 Bad Request: If no tickers are provided.
    """
    tickers = request.args.get('tickers')

    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    tickers = set(tickers.split(','))

    companies = Company.query.filter(Company.stock_ticker.in_(tickers)).all()
    all_articles = []
    for company in companies:
        articles = Article.query.with_parent(company).order_by(desc(Article.published)).limit(10).all()
        for article in articles:
            all_articles.append({
                "ticker": company.stock_ticker,
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
            })

    return jsonify({'articles': all_articles})

@views.route('/api/get/notifications', methods=['GET'])
@login_required
@handle_api_sqlalchemy_error('Error retrieving notifications.')
def get_notifs():
    """
    Retrieves unread notifications for the current user.

    Returns:
        A JSON response containing a list of unread notifications.
        Each notification is represented as a dictionary with the following keys:
        - id: The unique identifier of the notification.
        - message: The content of the notification message.
        - time: The timestamp when the notification was created.
    """
    notifications = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).order_by(desc(Notification.time)).all()
    notif_list = [{"id": notif.id, "message": notif.message,
                   "time": notif.time.strftime('%Y-%m-%d %H:%M:%S')}
                  for notif in notifications]

    return jsonify(notif_list)

@views.route('/api/delete/notifications', defaults={'notification_id': None}, methods=['DELETE'])
@views.route('/api/delete/notification/<int:notification_id>', methods=['DELETE'])
@login_required
@handle_api_sqlalchemy_error
def delete_notifications(notification_id):
    """
    Deletes notifications from the database.

    Args:
        notification_id (int): The ID of the notification to be deleted. If None, all notifications for the current user
                               that are unread will be deleted.

    Returns:
        A JSON response with the status of the deletion operation. If successful, the status will be 'success'.
        If the notification is not found, the status will be 'error' and a message will be included.
    """
    if notification_id is None:
        # No ID provided, delete all notifications
        Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.read == False
        ).delete()
        db.session.commit()
        return jsonify({'status': 'success'})

    # ID provided, delete specific notification
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.id:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Notification not found'}), 404
