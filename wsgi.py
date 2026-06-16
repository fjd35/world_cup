"""
WSGI entry point for the World Cup web application.

This file exposes the Flask application for WSGI servers like Gunicorn, uWSGI, etc.
"""

from src import app
from src.tasks import start_match_polling_scheduler

if app.config.get("MATCH_POLLING_ENABLED", True):
    start_match_polling_scheduler(app)

if __name__ == "__main__":
    app.run()
