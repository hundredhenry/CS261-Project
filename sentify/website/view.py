from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import User, Company
from .token import generate_confirmation_token, confirm_token
from .email import send_email

import re 

views = Blueprint("views", __name__)

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
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]{2,}$)", email):
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
            except SQLAlchemyError as e:
                abort(500, "Unable to continue with registration. Please return to homepage and try again.")
            if user_exists:
                flash("This email is already registered!", category="email_error")
                return redirect(url_for("views.register"))
            new_user = User(firstname=name, email=email, password_hash=generate_password_hash(password))# create a new user with generate_password_hash(password) default values are sufficient
            # add this user to the DB
            db.session.add(new_user)
            db.session.commit()
            # begin user verification via email check
            # do email sending process here
            token = generate_confirmation_token(email)
            confirm_url = url_for('views.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email - Sentify"
            
            send_email(subject, email, html)
            
            return redirect(url_for("views.unconfirmed"))

    return render_template('register.html')

@views.route('/unconfirmed/')
def unconfirmed():
    return render_template('unconfirmed.html')

@views.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', category='error')
    user = User.query.filter_by(email=email).first()
    
    if user:
        if user.verified:
            flash('Account already confirmed. Please login.', category='success')
            return redirect('/login')
        else:
            user.verified = True
            db.session.add(user)
            db.session.commit()
            flash('You have confirmed your account. Please login.', category='success')
        return redirect('/login')
        

@views.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and not user.verified:
            flash("Please verify your email first!", category="verify_error")
        else:
            if user and check_password_hash(user.password_hash, password):
                flash("Logged in successfully", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.landing"))
            else:
                flash("Email or password is incorrect!", category="login_error")
    return render_template('login.html')

@views.route('/resend/', methods=['GET', 'POST'])
def resend_email():
    if current_user.is_authenticated:
        return redirect(url_for("views.landing"))
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_confirmation_token(email)
            confirm_url = url_for('views.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email - Sentify"
            
            send_email(subject, email, html)
            return redirect(url_for("views.unconfirmed"))
        else:
            flash('This email is not registered!', category='email_error')

    return render_template('resend.html')
    
@views.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.landing"))

@views.route('/companies/')
def companies():
    return render_template('company_search.html')

@views.route('/retrieve_companies/', methods=['GET'])
def retrieve_companies():
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            companies = Company.query.with_entities(Company.stock_ticker, Company.company_name).all()
            results = [{'stock_ticker': company.stock_ticker, 'company_name': company.company_name} for company in companies]
            return jsonify(results)
        except SQLAlchemyError as e:
            attempts += 1
            if attempts == max_attempts:
                return jsonify({'error': f'Maximum number of attempts reached. Error: {str(e)}'}), 500