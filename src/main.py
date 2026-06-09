from __future__ import annotations

from typing import cast

import pandas as pd
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Fixture, Prediction, User

main = Blueprint("main", __name__)


def _current_user() -> User:
    return cast(User, current_user)


def _predictions_by_fixture(predictions: list[Prediction]) -> dict[int, Prediction]:
    return {prediction.fixture_id: prediction for prediction in predictions}

@main.route("/")
def index():
    users = db.session.query(User).order_by(User.score.desc(), User.username).all()
    df = get_summary_df()
    return render_template("index.html", users=users, df=df)

@main.route("/my_predictions")
@login_required
def my_predictions():
    user = _current_user()
    df = get_predictions_df()
    return render_template("my_predictions.html", user=user, df=df)

@main.route("/add_prediction", methods=["POST"])
@login_required
def add_prediction():
    user = _current_user()
    fixture_id = int(request.form["fixture_id"])
    score1 = int(request.form["score1"])
    score2 = int(request.form["score2"])
    existing_prediction = db.session.query(Prediction).filter_by(user_id=user.id, fixture_id=fixture_id).first()
    if existing_prediction is not None:
        print(f"Updating prediction {existing_prediction} with data {request.form}")
        existing_prediction.score1 = score1
        existing_prediction.score2 = score2
        db.session.commit()
    else:
        new_prediction = Prediction(user_id=user.id, fixture_id=fixture_id, score1=score1, score2=score2)
        db.session.add(new_prediction)
        db.session.commit()
        print(f"Adding prediction: {new_prediction}")
    return redirect(url_for("main.my_predictions"))

@main.route("/admin")
@login_required
def admin():
    user = _current_user()
    if user.id != 1:
        abort(403)
    return render_template("admin.html", fixturees=db.session.query(Fixture).order_by(Fixture.id).all())

@main.route("/update_fixture", methods=["POST"])
@login_required
def update_fixture():
    user = _current_user()
    if user.id != 1:
        abort(403)
    fixture_id = int(request.form["fixture_id"])
    fixture = db.session.get(Fixture, fixture_id)
    assert fixture is not None
    score1 = request.form["score1"]
    score2 = request.form["score2"]
    print(f"Updating fixture {fixture} with data {request.form}")
    fixture.score1 = int(score1) if score1 != "" else None
    fixture.score2 = int(score2) if score2 != "" else None
    fixture.is_finished = "lock" in request.form
    db.session.commit()
    update_scores()
    return redirect(url_for("main.admin"))

@main.route("/update_scores")
@login_required
def update_scores_route():
    user = _current_user()
    if user.id != 1:
        abort(403)
    update_scores()
    return redirect(url_for("main.admin"))

@main.errorhandler(403)
def forbidden(_exc: Exception):
    return render_template("403.html")

def get_summary_df() -> pd.DataFrame:
    fixtures = db.session.query(Fixture).filter_by(is_finished=True).order_by(Fixture.id).all()
    users = db.session.query(User).order_by(User.id).all()
    columns = ["Team 1", "Score", "Team 2"] + [user.username for user in users]
    data = []
    prediction_maps = [_predictions_by_fixture(user.predictions) for user in users]
    for fixture in fixtures:
        row = [fixture.team1, (fixture.score1 if fixture.score1 is not None else "", fixture.score2 if fixture.score2 is not None else ""), fixture.team2]
        for prediction_map in prediction_maps:
            prediction = prediction_map.get(fixture.id)
            if prediction is None:
                row.append(("", ""))
            else:
                row.append((prediction.score1, prediction.score2))
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df

def get_predictions_df() -> pd.DataFrame:
    fixtures = db.session.query(Fixture).order_by(Fixture.id).all()
    columns = ["fixture", "predicted_score"]
    data = []
    user = _current_user()
    predictions = _predictions_by_fixture(user.predictions)
    for fixture in fixtures:
        prediction = predictions.get(fixture.id)
        if prediction is None:
            prediction_score = ("", "")
        else:
            prediction_score = (prediction.score1, prediction.score2)
        row = [fixture, prediction_score]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df

def update_scores():
    users = db.session.query(User).order_by(User.id).all()
    fixtures = db.session.query(Fixture).order_by(Fixture.id).all()
    user_scores = {user.id: 0 for user in users}
    prediction_maps = {user.id: _predictions_by_fixture(user.predictions) for user in users}
    for fixture in fixtures:
        if fixture.score1 is None or fixture.score2 is None:
            break
        for user in users:
            prediction = prediction_maps[user.id].get(fixture.id)
            if prediction is None:
                continue
            predicted_gd = prediction.score1 - prediction.score2
            actual_gd = fixture.score1 - fixture.score2
            if prediction.score1 == fixture.score1 and prediction.score2 == fixture.score2:
                user_scores[user.id] += 3
            elif predicted_gd == actual_gd != 0:
                user_scores[user.id] += 2
            elif sign(predicted_gd) == sign(actual_gd):
                user_scores[user.id] += 1
    for user in users:
        user.score = user_scores[user.id]
    db.session.commit()
    print(f"Updated scores: {users}")

def sign(x):
    if x > 0:
        return 1
    if x == 0:
        return 0
    if x < 0:
        return -1