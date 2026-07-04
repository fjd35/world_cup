import argparse
import random
from typing import Callable
import json
import re

from werkzeug.security import generate_password_hash
import numpy as np

from src import app, db
from src.models import Fixture, Prediction, User

ScorePredictorCallable = Callable[[str, str], tuple[int, int] | tuple[None, None]]


def get_prediction_from_file(
        team_1: str, 
        team_2: str, 
        filename: str = "last_32_16_predictions.json"
    ) -> tuple[int, int] | tuple[None, None]:
    if not team_1 or not team_2:
        return None, None
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for match in data["predictions"]:
        home = match["home"]
        away = match["away"]

        home_goals = int(match["home_score"])
        away_goals = int(match["away_score"])

        if home == team_1 and away == team_2:
            return home_goals, away_goals

        if home == team_2 and away == team_1:
            return away_goals, home_goals

    print(
        f"No prediction found for fixture '{team_1}' vs '{team_2}'"
    )
    return None, None

def random_match_score(home_team: str, away_team: str, rng=None) -> tuple[int, int] | tuple[None, None]:
    if rng is None:
        rng = np.random.default_rng()

    base = rng.gamma(shape=4.0, scale=0.33)      # match openness
    advantage = rng.normal(0.0, 0.35)  # one side better on the day

    home_rate = base * np.exp(advantage)
    away_rate = base * np.exp(-advantage)

    return (
        rng.poisson(home_rate),
        rng.poisson(away_rate)
    )

def create_custom_user(
        username: str, 
        password: str,
        score_predictor: ScorePredictorCallable,
    ) -> None:
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username, password=generate_password_hash(password, method="scrypt"))
            db.session.add(user)
            db.session.commit()
            print(f"Created user '{username}' with password '{password}'")
        else:
            print(f"User '{username}' already exists")

        fixtures: list[Fixture] = (
            Fixture.query
            .order_by(Fixture.id)
            .all()
        )

        if not fixtures:
            print("No fixtures found to seed predictions.")
            return

        inserted = 0
        updated = 0
        for fixture in fixtures:
            home_team = fixture.home_team.name if fixture.home_team else ""
            away_team = fixture.away_team.name if fixture.away_team else ""
            score1, score2 = score_predictor(
                home_team,
                away_team,
            )
            if score1 is None or score2 is None:
                print(f"Skipping fixture '{home_team}' vs '{away_team}' due to missing prediction.")
                continue

            prediction = Prediction.query.filter_by(user_id=user.id, fixture_id=fixture.id).first()
            if prediction is None:
                prediction = Prediction(user_id=user.id, fixture_id=fixture.id, score1=score1, score2=score2)
                db.session.add(prediction)
                inserted += 1
            else:
                prediction.score1 = score1
                prediction.score2 = score2
                updated += 1

        db.session.commit()
        print(f"Seeded predictions for {len(fixtures)} fixtures: {inserted} inserted, {updated} updated.")


if __name__ == "__main__":
    username = "ChatGPT"
    password = "password"
    score_predictor = get_prediction_from_file
    create_custom_user(
        username=username, 
        password=password,
        score_predictor=score_predictor,
    )
