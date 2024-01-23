from flask import Blueprint, render_template

views = Blueprint("views", __name__)

@views.route('/')
def test_page():
    return render_template('index.html')