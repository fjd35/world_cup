from __future__ import annotations

from typing import Any, cast
from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import selectinload

from . import db
from .api_football import FootballDataError, sync_world_cup_fixtures
from .models import Fixture, Prediction, User

STAGES = [
    "GROUP_STAGE",
    "LAST_32",
    "LAST_16",
    "QUARTER_FINALS",
    "SEMI_FINALS",
    "THIRD_PLACE",
    "FINAL",
]

def pretty_format(s: str | None) -> str:
    if s is None:
        return ""
    return s.replace("_", " ").title()

main = Blueprint("main", __name__)


def _current_user() -> User:
    return cast(User, current_user)


def _predictions_by_fixture(predictions: list[Prediction]) -> dict[int, Prediction]:
    return {prediction.fixture_id: prediction for prediction in predictions}


def _group_fixtures_by_stage(items: list[Any]) -> list[tuple[str | None, list[Any]]]:
    """
    Group items by their stage (api_round attribute).
    Returns a list of tuples (stage_name, items_list) ordered by STAGES, then remaining stages.
    """
    from collections import defaultdict
    groups: dict[str | None, list[Any]] = defaultdict(list)
    for item in items:
        # Handle different data structures (Fixture object, dict with 'fixture' key, etc.)
        if isinstance(item, Fixture):
            fixture = item
        elif isinstance(item, dict):
            fixture = item.get("fixture", item)
        else:
            fixture = item
        stage = fixture.api_round if hasattr(fixture, "api_round") else None
        groups[stage].append(item)

    grouped_fixtures: list[tuple[str | None, list[Any]]] = []
    # Add stages in desired order if present
    for stage in STAGES:
        if stage in groups:
            grouped_fixtures.append((pretty_format(stage), groups.pop(stage)))

    # Append any remaining stages (preserve their insertion order)
    for stage, items_list in groups.items():
        grouped_fixtures.append((pretty_format(stage), items_list))

    return grouped_fixtures


def score_points(predicted_score: tuple[int, int], actual_score: tuple[int, int]) -> int:
    predicted_gd = predicted_score[0] - predicted_score[1]
    actual_gd = actual_score[0] - actual_score[1]
    if predicted_score == actual_score:
        return 3
    if predicted_gd == actual_gd:
        return 2
    if sign(predicted_gd) == sign(actual_gd):
        return 1
    return 0


def score_class(
        predicted_score: tuple[int, int], 
        actual_score: tuple[int, int],
    ) -> str:
    if (
        None in predicted_score or 
        None in actual_score or 
        "" in predicted_score or
        "" in actual_score
    ):
        return ""
    predicted_tuple = (int(predicted_score[0]), int(predicted_score[1]))
    actual_tuple = (int(actual_score[0]), int(actual_score[1]))
    points = score_points(predicted_tuple, actual_tuple)
    return f"points{points}"

@main.route("/")
def index():
    users = db.session.query(User).order_by(User.score.desc(), User.username).all()
    summary_rows, usernames = get_summary_rows()
    
    grouped_fixtures = _group_fixtures_by_stage(summary_rows)
    
    return render_template(
        "index.html",
        users=users,
        grouped_fixtures=grouped_fixtures,
        df_columns=usernames,
        score_class=score_class,
    )

@main.route("/my_predictions")
@login_required
def my_predictions():
    user = _current_user()
    # Build fixtures with user's predictions
    fixtures = (
        db.session.query(Fixture)
        .options(selectinload(Fixture.home_team), selectinload(Fixture.away_team))
        .order_by(Fixture.start_at, Fixture.id)
        .all()
    )
    predictions_map = _predictions_by_fixture(user.predictions)

    # Convert to list of dicts with fixture and predicted_score
    items = []
    for fixture in fixtures:
        pred = predictions_map.get(fixture.id)
        predicted_score = (pred.score1, pred.score2) if pred is not None else ("", "")
        items.append({"fixture": fixture, "predicted_score": predicted_score})

    # Group by stage
    grouped_fixtures = _group_fixtures_by_stage(items)

    return render_template("my_predictions.html", user=user, grouped_fixtures=grouped_fixtures)

@main.route("/add_prediction", methods=["POST"])
@login_required
def add_prediction():
    user = _current_user()
    fixture_id = int(request.form["fixture_id"])
    score1 = int(request.form["score1"])
    score2 = int(request.form["score2"])
    fixture = db.session.get(Fixture, fixture_id)
    if fixture is None:
        abort(404)
    if fixture.has_started or fixture.home_team_id is None or fixture.away_team_id is None:
        abort(400)
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
    # Redirect back to the user's predictions page and anchor to the edited fixture
    return redirect(url_for("main.my_predictions") + f"#fixture-{fixture_id}")

@main.route("/account")
@login_required
def account():
    user = _current_user()
    return render_template("my_account.html", user=user)

@main.route("/account", methods=["POST"])
@login_required
def update_account():
    user = _current_user()
    current_password = request.form.get("current_password", "")
    if not current_password:
        flash("Current password is required to make changes.")
        return redirect(url_for("main.account"))

    if not check_password_hash(str(user.password), str(current_password)):
        flash("Current password is incorrect.")
        return redirect(url_for("main.account"))

    new_username = request.form.get("username", "").strip()
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not new_username:
        flash("Username cannot be blank.")
        return redirect(url_for("main.account"))

    changed = False

    if new_username != user.username:
        existing = db.session.query(User).filter_by(username=new_username).first()
        if existing is not None:
            flash("That username is already taken.")
            return redirect(url_for("main.account"))
        user.username = new_username
        changed = True
        flash("Username updated.")

    if new_password or confirm_password:
        if new_password != confirm_password:
            flash("New password and confirm password do not match.")
            return redirect(url_for("main.account"))
        if not new_password:
            flash("New password cannot be empty.")
            return redirect(url_for("main.account"))
        user.password = generate_password_hash(str(new_password), method="scrypt")
        changed = True
        flash("Password updated.")

    if not changed:
        flash("No changes were made.")
        return redirect(url_for("main.account"))

    db.session.commit()
    return redirect(url_for("main.account"))

@main.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    user = _current_user()
    current_password = request.form.get("current_password", "")
    if not current_password or not check_password_hash(str(user.password), str(current_password)):
        flash("Current password is required and must be correct to delete your account.")
        return redirect(url_for("main.account"))

    db.session.query(Prediction).filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash("Your account and predictions have been deleted.")
    return redirect(url_for("main.index"))

@main.route("/admin")
@login_required
def admin():
    user = _current_user()
    if user.id != 1:
        abort(403)
    fixtures = (
        db.session.query(Fixture)
        .options(selectinload(Fixture.home_team), selectinload(Fixture.away_team))
        .order_by(Fixture.start_at, Fixture.id)
        .all()
    )
    users = db.session.query(User).order_by(User.id).all()

    # Group fixtures by stage
    grouped_fixtures = _group_fixtures_by_stage(fixtures)

    return render_template("admin.html", grouped_fixtures=grouped_fixtures, users=users)

@main.route("/update_fixture", methods=["POST"])
@login_required
def update_fixture():
    user = _current_user()
    if user.id != 1:
        abort(403)
    fixture_id = int(request.form["fixture_id"])
    fixture = db.session.get(Fixture, fixture_id)
    assert fixture is not None
    home_score = request.form.get("home_score", "")
    away_score = request.form.get("away_score", "")
    print(f"Updating fixture {fixture} with data {request.form}")
    fixture.home_score = int(home_score) if home_score != "" else None
    fixture.away_score = int(away_score) if away_score != "" else None
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


@main.route("/admin/delete_user", methods=["POST"])
@login_required
def delete_user():
    user = _current_user()
    if user.id != 1:
        abort(403)
    user_id = int(request.form["user_id"])
    if user_id == 1:
        flash("Cannot delete the admin user.")
        return redirect(url_for("main.admin"))
    target_user = db.session.get(User, user_id)
    if target_user is None:
        abort(404)
    db.session.query(Prediction).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.session.delete(target_user)
    db.session.commit()
    flash(f"Deleted user {target_user.username} and all their predictions.")
    return redirect(url_for("main.admin"))


@main.route("/admin/import_world_cup_fixtures", methods=["POST"])
@login_required
def import_world_cup_fixtures():
    user = _current_user()
    if user.id != 1:
        abort(403)
    competition_code = request.form.get("competition_code", "WC").strip().upper() or "WC"
    season_text = request.form.get("season", "2026")
    try:
        season = int(season_text)
    except ValueError:
        flash("Season must be a number.")
        return redirect(url_for("main.admin"))
    try:
        result = sync_world_cup_fixtures(season=season, competition_code=competition_code)
    except FootballDataError as exc:
        flash(str(exc))
    else:
        flash(
            f"Imported {result.inserted} new fixtures and updated {result.updated} existing fixtures for {result.competition_name} {result.season}."
        )
    update_scores()
    return redirect(url_for("main.admin"))

@main.errorhandler(403)
def forbidden(_exc: Exception):
    return render_template("403.html"), 403

def get_summary_rows() -> tuple[list[dict[str, Any]], list[str]]:
    now_utc = datetime.now(timezone.utc).isoformat()
    fixtures = (
        db.session.query(Fixture)
        .options(selectinload(Fixture.home_team), selectinload(Fixture.away_team))
        .filter(Fixture.start_at.isnot(None), Fixture.start_at <= now_utc)
        .order_by(Fixture.id)
        .all()
    )
    users = db.session.query(User).order_by(User.id).all()
    usernames = [user.username for user in users]
    prediction_maps = [_predictions_by_fixture(user.predictions) for user in users]

    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        row: dict[str, Any] = {"fixture": fixture}
        for user, prediction_map in zip(users, prediction_maps):
            prediction = prediction_map.get(fixture.id)
            row[user.username] = (
                (prediction.score1, prediction.score2)
                if prediction is not None
                else ("", "")
            )
        rows.append(row)

    return rows, usernames


def update_scores():
    users = db.session.query(User).order_by(User.id).all()
    fixtures = db.session.query(Fixture).filter(Fixture.home_score.isnot(None), Fixture.away_score.isnot(None)).order_by(Fixture.id).all()
    user_scores = {user.id: 0 for user in users}
    prediction_maps = {user.id: _predictions_by_fixture(user.predictions) for user in users}
    for fixture in fixtures:
        if fixture.home_score is None or fixture.away_score is None:
            break
        for user in users:
            prediction = prediction_maps[user.id].get(fixture.id)
            if prediction is None:
                continue
            user_scores[user.id] += score_points((prediction.score1, prediction.score2), (fixture.home_score, fixture.away_score))
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