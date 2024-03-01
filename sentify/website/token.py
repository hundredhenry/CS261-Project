from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_confirmation_token(email):
    serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    return serialiser.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=600):
    serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    email = serialiser.loads(
        token,
        salt=current_app.config['SECURITY_PASSWORD_SALT'],
        max_age=expiration
    )
    
    return email