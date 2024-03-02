from website import create_app
from system import NewsSystem

app = create_app()
news_system = NewsSystem()

if __name__ == "__main__":
    with app.app_context():
        news_system.update_companies_desc()
        news_system.update_companies()
    app.run(debug=1)