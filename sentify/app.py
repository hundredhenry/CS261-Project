from website import create_app, socketio
from system import NewsSystem

app = create_app()
with app.app_context():
    news_system = NewsSystem()

def backlog():
    with app.app_context():
        news_system.update_companies_desc()
        news_system.backlog()   

def update_companies():
    with app.app_context():
        news_system.update_companies_desc()
        news_system.update_companies()
        
if __name__ == "__main__":
    socketio.start_background_task(update_companies)
    socketio.run(app) 