import pandas as pd
from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user

from . import db
from .models import *

main = Blueprint("main", __name__)

@main.route("/")
def index():
    users = db.session.query(User).order_by(User.score.desc(), User.username).all()
    df = get_summary_df()
    return render_template("index.html", users=users, df=df)

@main.route("/my_predictions")
@login_required
def my_predictions():
    df = get_predictions_df()
    return render_template("my_predictions.html", user=current_user, df=df)

@main.route("/add_prediction", methods=["POST"])
@login_required
def add_prediction():
    data = request.form
    existing_prediction = db.session.query(Prediction).filter_by(user_id=current_user.id, fixture_id=data["fixture_id"]).first()
    if existing_prediction:
        print(f"Updating prediction {existing_prediction} with data {data}")
        existing_prediction.score1 = data["score1"]
        existing_prediction.score2 = data["score2"]
        db.session.commit()
    else:
        new_prediction = Prediction(user_id=current_user.id, fixture_id=data["fixture_id"], score1=data["score1"], score2=data["score2"])
        db.session.add(new_prediction)
        db.session.commit()
        print(f"Adding prediction: {new_prediction}")
    return redirect(url_for("main.my_predictions"))

@main.route("/admin")
@login_required
def admin():
    if current_user.id != 1:
        abort(403)
    return render_template("admin.html", fixturees=db.session.query(Fixture).order_by(Fixture.id).all())

@main.route("/update_fixture", methods=["POST"])
@login_required
def update_fixture():
    if current_user.id != 1:
        abort(403)
    data = request.form
    fixture = db.session.query(Fixture).get(data["fixture_id"])
    print(f"Updating fixture {fixture} with data {data}")
    fixture.score1 = data["score1"] if data["score1"] != '' else None
    fixture.score2 = data["score2"] if data["score2"] != '' else None
    fixture.is_finished = "lock" in data
    db.session.commit()
    update_scores()
    return redirect(url_for("main.admin"))

@main.route("/update_scores")
@login_required
def update_scores_route():
    if current_user.id != 1:
        abort(403)
    update_scores()
    return redirect(url_for("main.admin"))

@main.route("/add_fixture", methods=["POST"])
@login_required
def add_fixture():
    if current_user.id != 1:
        abort(403)
    data = request.form
    new_fixture = Fixture(team1=data["team1"], team2=data["team2"])
    db.session.add(new_fixture)
    db.session.commit()
    return redirect(url_for("main.admin"))
    

@main.errorhandler(403)
def forbidden(e):
    return render_template("403.html")

def get_summary_df() -> pd.DataFrame:
    fixturees = db.session.query(Fixture).filter(Fixture.is_finished == True).order_by(Fixture.id).all()
    users = db.session.query(User).order_by(User.id).all()
    columns = ["Team 1", "Score", "Team 2"] + [user.username for user in users]
    data = []
    for fixture in fixturees:
        row = [
            fixture.team1, 
            (
                fixture.score1 if fixture.score1 is not None else "", 
                fixture.score2 if fixture.score2 is not None else ""
            ), 
            fixture.team2
        ]
        for user in users:
            try:
                prediction = next(filter(lambda p: p.fixture.id == fixture.id, user.predictions))
            except StopIteration:
                row += [('', '')]
            else:
                row += [(prediction.score1, prediction.score2)]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df

def get_predictions_df() -> pd.DataFrame:
    fixturees = db.session.query(Fixture).order_by(Fixture.id).all()
    columns = ["fixturees", "prediction_scores"]
    data = []
    for fixture in fixturees:
        try:
            prediction = next(filter(lambda p: p.fixture.id == fixture.id, current_user.predictions))
        except StopIteration:
            prediction_score = ('', '')
        else:
            prediction_score = (prediction.score1, prediction.score2)
        row = [fixture, prediction_score]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df

def update_scores():
    users = db.session.query(User).order_by(User.id).all()
    fixturees = db.session.query(Fixture).order_by(Fixture.id).all()
    user_scores = {user.id: 0 for user in users}
    for fixture in fixturees:
        if fixture.score1 is None or fixture.score2 is None:
            break
        for user in users:
            try:
                prediction = next(filter(lambda p: p.fixture.id == fixture.id, user.predictions))
            except StopIteration:
                continue
            if prediction.score1 is None or prediction.score2 is None:
                # Shouldn't be possible but worth filtering anyway
                continue
            predicted_gd = prediction.score1 - prediction.score2
            actual_gd = fixture.score1 - fixture.score2
            if prediction.score1 == fixture.score1 and prediction.score2 == fixture.score2:
                # 3 points for a perfectly predicted score
                user_scores[user.id] += 3
            elif predicted_gd == actual_gd != 0:
                # 2 points for guessing goal difference (draw not incl.)
                user_scores[user.id] += 2
            elif sign(predicted_gd) == sign(actual_gd):
                # 1 point for guessing result
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