from threading import Thread

from website import create_app
from system import NewsSystem

app = create_app()

def update_companies():
    with app.app_context():
        news_system = NewsSystem()
        news_system.update_companies_desc()
        news_system.update_companies()
        
if __name__ == "__main__":
    thread = Thread(target=update_companies)
    thread.start()
    app.run(debug=1)