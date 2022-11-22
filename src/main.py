import pandas as pd
from flask import Blueprint, render_template, redirect, url_for
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
def add_prediction(match_id: int, score1: int, score2: int):
    new_prediction = Prediction(user_id=current_user.id, match_id=match_id, score1=score1, score2=score2)
    db.session.add(new_prediction)
    db.session.commit()
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
                row += [(None, None)]
            else:
                row += [(prediction.score1, prediction.score2)]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df

def get_predictions_df() -> pd.DataFrame:
    matches = db.session.query(Match).order_by(Match.id).all()
    columns = ["Team 1", "Your prediction", "Team 2", "Editable"]
    data = []
    for match in matches:
        try:
            prediction = next(filter(lambda p: p.match.id == match.id, current_user.predictions))
        except StopIteration:
            prediction_score = (None, None)
        else:
            prediction_score = (prediction.score1, prediction.score2)
        row = [match.team1, prediction_score, match.team2, not bool(match.is_finished)]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    return df