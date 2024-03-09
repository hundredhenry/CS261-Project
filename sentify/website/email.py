from flask_mail import Message
from flask import current_app

from . import mail

def send_email(subject, to, html_body):
    """
    Sends an email with the specified subject, recipient, and HTML body.

    Parameters:
    - subject (str): The subject of the email.
    - to (str): The recipient's email address.
    - html_body (str): The HTML content of the email body.

    Returns:
    None
    """
    msg = Message(
        subject,
        recipients=[to],
        html=html_body,
        sender=current_app.config['MAIL_USERNAME'])
    mail.send(msg)
