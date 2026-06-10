import argparse
import random

from werkzeug.security import generate_password_hash
import numpy as np

from src import app, db
from src.models import Fixture, Prediction, User

def random_match_score(rng=None):
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

def create_random_user(username: str, password: str) -> None:
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username, password=generate_password_hash(password, method="scrypt"))
            db.session.add(user)
            db.session.commit()
            print(f"Created user '{username}' with password '{password}'")
        else:
            print(f"User '{username}' already exists")

        fixtures = (
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
            score1, score2 = random_match_score()
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
        print(f"Seeded random predictions for {len(fixtures)} fixtures: {inserted} inserted, {updated} updated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a random-prediction user and insert predictions for every fixture.")
    parser.add_argument("--username", default="Randotron", help="Username for the random prediction user")
    parser.add_argument("--password", default="password", help="Password for the random prediction user")
    args = parser.parse_args()
    create_random_user(username=args.username, password=args.password)
