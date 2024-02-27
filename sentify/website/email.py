from flask_mail import Message
from . import mail
from flask import current_app

def send_email(subject, to, html_body):
    msg = Message(
        subject,
        recipients=[to],
        html=html_body,
        sender=current_app.config['MAIL_USERNAME'])
    mail.send(msg)