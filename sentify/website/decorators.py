from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from flask import flash, redirect, url_for, jsonify
from . import db

def handle_sqlalchemy_error(redirect_url, error_message):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SQLAlchemyError:
                db.session.rollback()
                flash(error_message, 'error')
                return redirect(url_for(redirect_url))
        return decorated_function
    return decorator

def handle_api_sqlalchemy_error(error_message):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SQLAlchemyError:
                db.session.rollback()
                return jsonify({'error': error_message}), 500
        return decorated_function
    return decorator