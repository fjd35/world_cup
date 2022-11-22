import pandas as pd
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from . import db
from .models import *

main = Blueprint("main", __name__)

@main.route("/")
def index():
    df = get_summary_df()
    return render_template("index.html", df=df)

@main.route("/my_predictions")
@login_required
def my_predictions():
    df = get_predictions_df()
    return render_template("my_predictions.html", user=current_user, df=df)

@main.route("/add_prediction", methods=["POST"])
def add_prediction():
    data = request.form
    existing_prediction = db.session.query(Prediction).filter_by(user_id=current_user.id, match_id=data["match_id"]).first()
    if existing_prediction:
        existing_prediction.score1 = data["score1"]
        existing_prediction.score2 = data["score2"]
        print(f"Updating prediction: {existing_prediction}")
        db.session.commit()
    else:
        new_prediction = Prediction(user_id=current_user.id, match_id=data["match_id"], score1=data["score1"], score2=data["score2"])
        db.session.add(new_prediction)
        db.session.commit()
        print(f"Adding prediction: {new_prediction}")
    return redirect(url_for("main.my_predictions"))

def get_summary_df() -> pd.DataFrame:
    matches = db.session.query(Match).filter(Match.is_finished == True).order_by(Match.id).all()
    users = db.session.query(User).order_by(User.id).all()
    columns = ["Team 1", "Score", "Team 2"] + [user.username for user in users]
    data = []
    for match in matches:
        row = [match.team1, (match.score1, match.score2), match.team2]
        for user in users:
            try:
                prediction = next(filter(lambda p: p.match.id == match.id, user.predictions))
            except StopIteration:
                row += [('', '')]
            else:
                row += [(prediction.score1, prediction.score2)]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df

def get_predictions_df() -> pd.DataFrame:
    matches = db.session.query(Match).order_by(Match.id).all()
    columns = ["matches", "prediction_scores"]
    data = []
    for match in matches:
        try:
            prediction = next(filter(lambda p: p.match.id == match.id, current_user.predictions))
        except StopIteration:
            prediction_score = ('', '')
        else:
            prediction_score = (prediction.score1, prediction.score2)
        row = [match, prediction_score]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df