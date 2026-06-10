"""
WSGI entry point for the World Cup web application.

This file exposes the Flask application for WSGI servers like Gunicorn, uWSGI, etc.
"""

from src import app

if __name__ == "__main__":
    app.run()
