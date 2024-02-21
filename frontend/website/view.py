from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User
from .token import generate_confirmation_token, confirm_token
from .email import send_email

import re 

views = Blueprint("views", __name__)

@views.route('/')
def test_page():
    return render_template('index.html')

@views.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == "POST":                
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # check if the user is already registered 
        user_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash("This email is already registered!", category="error")
            return redirect(url_for("views.test_page"))
        # if not, continue registering the user
        
        if not re.match("^[a-zA-Z]*$", name):
            flash('Name must contain only letters', category='error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address', category='error')
        elif password != confirm_password:
            flash('Passwords do not match', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
        else:
            new_user = User(firstname=name, email=email, password_hash=generate_password_hash(password))# create a new user with generate_password_hash(password) default values are sufficient
            # add this user to the DB
            db.session.add(new_user)
            db.session.commit()
            # begin user verification via email check
            flash("User has been registered, please activate your account", category="success")
            # do email sending process here
            token = generate_confirmation_token(email)
            confirm_url = url_for('views.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email - Sentify"
            
            send_email(subject, email, html)
            
            flash('A confirmation email has been sent via email.', 'success')

            return render_template('unconfirmed.html')

    return render_template('register.html')

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
            flash("Please verify your email first", category="error")
            print("Please verify your email first")
            return redirect(url_for("views.test_page"))
        
        if user and check_password_hash(user.password_hash, password):
            flash("Logged in successfully", category="success")
            print("Logged in successfully")
            return redirect(url_for("views.test_page"))
        else:
            flash("Email or password is incorrect", category="error")
            print("Email or password is incorrect")
    return render_template('login.html')
    
    

