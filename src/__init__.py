import os

from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

app.config.update(
    SECRET_KEY="AnActualSecretKey",
    SQLALCHEMY_DATABASE_URI="sqlite:///../db.sqlite",
    FOOTBALL_DATA_BASE_URL=os.getenv("FOOTBALL_DATA_BASE_URL", "https://api.football-data.org/v4"),
    FOOTBALL_DATA_TOKEN=os.getenv("FOOTBALL_DATA_TOKEN", "3523264a8ffe4cf89782297f6d5504a6"),
    FOOTBALL_DATA_TOKEN_HEADER=os.getenv("FOOTBALL_DATA_TOKEN_HEADER", "X-Auth-Token"),
    FOOTBALL_DATA_TIMEOUT=float(os.getenv("FOOTBALL_DATA_TIMEOUT", "20")),
    MATCH_POLLING_ENABLED=os.getenv("MATCH_POLLING_ENABLED", "1") != "0",
    MATCH_POLL_INTERVAL_SECONDS=int(os.getenv("MATCH_POLL_INTERVAL_SECONDS", "60")),
    MATCH_POLLING_COMPETITION_CODE=os.getenv("MATCH_POLLING_COMPETITION_CODE", "WC"),
    MATCH_POLLING_SEASON=int(os.getenv("MATCH_POLLING_SEASON", "2026")),
)

login_manager = LoginManager()
login_manager.__dict__["login_view"] = "auth.login"
login_manager.init_app(app)

from .models import User
from .models import db, ensure_fixture_schema

@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))

db.init_app(app)

with app.app_context():
    ensure_fixture_schema()

# blueprint for auth routes in our app
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .main import score_class
app.jinja_env.globals.update(score_class=score_class)

