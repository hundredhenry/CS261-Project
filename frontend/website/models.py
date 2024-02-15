from website import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35))
    email = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(255))
    verified = db.Column(db.Boolean(), default=False, unique=False)
    