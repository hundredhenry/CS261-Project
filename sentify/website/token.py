from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app

def generate_confirmation_token(email):
    """
    Generates a confirmation token for the given email.

    Parameters:
    - email (str): The email address for which the confirmation token is generated.

    Returns:
    - str: The generated confirmation token.
    """
    serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serialiser.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=600):
    """
    Confirm the validity of a token and return the associated email.

    Parameters:
    - token (str): The token to be confirmed.
    - expiration (int): The maximum age of the token in seconds (default: 600).

    Returns:
    - str or None: The email associated with the token if it is valid and has not expired,
      or None if the token is invalid or has expired.
    """
    serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serialiser.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except (SignatureExpired, BadSignature):
        return None

    return email
