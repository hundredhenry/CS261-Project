from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re

views = Blueprint("views", __name__)

@views.route('/')
def test_page():
    return render_template('index.html')

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":                
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # check if the user is already registered 
        # if not, continue registering the user
        
        if not re.match("^[a-zA-Z]*$", name):
            flash('Name must contain only letters', category='error')
            print("Name must contain only letters") # debug msgs
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address', category='error')
            print("Invalid email address")
        elif password != confirm_password:
            flash('Passwords do not match', category='error')
            print("Passwords do not match")
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            print("Password must be at least 8 characters")
        else:
            new_user = None # create a new user with generate_password_hash(password) default values are sufficient
            # add this user to the DB
            
            # begin user verification via email check
            flash("User has been registered, please register your email", category="success")
            # do email sending process here
            return render_template('unconfirmed.html')

    return render_template('register.html')