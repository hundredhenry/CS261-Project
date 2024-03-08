from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from flask import flash, redirect, url_for, jsonify
from . import db

def handle_sqlalchemy_error(redirect_url, error_message):
    """
    Decorator function that handles SQLAlchemy errors by rolling back the session,
    flashing an error message, and redirecting to a specified URL.

    Args:
        redirect_url (str): The URL to redirect to in case of an error.
        error_message (str): The error message to display.

    Returns:
        The decorated function.
    """
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
    """
    Decorator function that handles SQLAlchemy errors in API endpoints.

    Args:
        error_message (str): The error message to be returned in the response.

    Returns:
        function: The decorated function.
    """
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