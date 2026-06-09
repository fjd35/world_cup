from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from . import db

auth = Blueprint("auth", __name__)
INVITATION_KEY = "DUGGANWC!"


def _form_value(name: str) -> str:
    value = request.form.get(name)
    return value if value is not None else ""

@auth.route("/login")
def login():
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login_post():
    username = _form_value("username")
    password = _form_value("password")
    remember = request.form.get("remember") is not None

    user: User | None = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(str(user.password), str(password)):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    return redirect(url_for("main.index"))

@auth.route("/signup")
def signup():
    return render_template("signup.html")

@auth.route("/signup", methods=["POST"])
def signup_post():
    key = _form_value("key")
    username = _form_value("username")
    password = _form_value("password")

    if key != INVITATION_KEY:
        flash("Invitation key incorrect")
        return redirect(url_for("auth.signup"))

    user = User.query.filter_by(username=username).first()

    if user is not None:
        flash("username address already exists")
        return redirect(url_for("auth.signup"))

    new_user = User(username=username, password=generate_password_hash(str(password), method="scrypt"))

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("auth.login"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))