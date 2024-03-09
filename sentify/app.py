"""
This module contains the main application for the website. 

It imports the Flask application instance from the `website` package 
and the `NewsSystem` from the `system` package. 

The `NewsSystem` is initialised within the application context,
and a function `update_companies` is defined to update the companies in the `NewsSystem`.

If this module is run directly,
it starts a background task to update the companies and runs the Flask application.

Functions:
    update_companies(do_backlog=False): Updates the companies in the news system.
"""

from website import create_app, socketio
from system import NewsSystem

app = create_app()
with app.app_context():
    news_system = NewsSystem()

def update_companies(do_backlog=False):
    """
    Updates the companies in the news system.

    Args:
        do_backlog (bool, optional): Whether to perform backlog processing. Defaults to False.
    """
    with app.app_context():
        news_system.update_companies_desc()
        if do_backlog:
            news_system.backlog()
        news_system.update_companies()

if __name__ == "__main__":
    socketio.start_background_task(update_companies)
    socketio.run(app)
