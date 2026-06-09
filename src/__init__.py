from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

app.config.update(
    SECRET_KEY="AnActualSecretKey",
    SQLALCHEMY_DATABASE_URI="sqlite:///../db.sqlite",
)

# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="fergal",
#     password="Hj!bZitag!Nb7si",
#     hostname="fergal.mysql.pythonanywhere-services.com",
#     databasename="fergal$WorldCup",
# )
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager()
login_manager.__dict__["login_view"] = "auth.login"
login_manager.init_app(app)

from .models import User
from .models import db

@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))

db.init_app(app)

# blueprint for auth routes in our app
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .main import sign
app.jinja_env.globals.update(sign=sign)

