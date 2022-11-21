from flask import Blueprint, render_template
from flask_login import login_required, current_user

from . import db
from .models import *

main = Blueprint("main", __name__)

@main.route("/")
def index():
    matches = db.session.query(Match).order_by(Match.id).all()
    return render_template("index.html", matches=matches)

@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.name)
