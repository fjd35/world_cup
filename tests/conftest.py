"""Shared test fixtures and configuration."""

import pytest
from werkzeug.security import generate_password_hash

# Temporarily modify the app config before importing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import app, db as flask_db
from src.models import User, Team, Fixture, Prediction


@pytest.fixture
def app_fixture():
    """Create and configure a test app instance."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        flask_db.create_all()
        yield app
        flask_db.session.remove()
        flask_db.drop_all()


@pytest.fixture
def client(app_fixture):
    """Create a test client for the app."""
    return app_fixture.test_client()


@pytest.fixture
def runner(app_fixture):
    """Create a CLI runner for the app."""
    return app_fixture.test_cli_runner()


@pytest.fixture
def db(app_fixture):
    """Return the database session for the test app."""
    with app_fixture.app_context():
        yield flask_db


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(username='admin', password=generate_password_hash('password123', method='scrypt'))
        user.id = 1  # Ensure admin user has id=1
        db.session.add(user)
        db.session.commit()

    return user


@pytest.fixture
def regular_user(db):
    """Create and return a regular user."""
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', password=generate_password_hash('password456', method='scrypt'))
        user.id = 2 # Ensure regular user is not admin
        db.session.add(user)
        db.session.commit()
    return user


@pytest.fixture
def teams(db):
    """Create and return sample teams."""
    team1 = Team(name='England', tla='ENG', api_team_id=1, crest_url='http://example.com/eng.png')
    team2 = Team(name='France', tla='FRA', api_team_id=2, crest_url='http://example.com/fra.png')
    team3 = Team(name='Germany', tla='GER', api_team_id=3, crest_url='http://example.com/ger.png')
    db.session.add_all([team1, team2, team3])
    db.session.commit()
    return [team1, team2, team3]


@pytest.fixture
def fixtures(db, teams):
    """Create and return sample fixtures."""
    from datetime import datetime, timezone, timedelta
    
    team1, team2, team3 = teams
    
    # Fixture in the past (has started)
    past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    fixture1 = Fixture(
        api_fixture_id=101,
        api_league_id=1,
        api_season=2026,
        api_round='GROUP_STAGE',
        start_at=past_time,
        home_team_id=team1.id,
        away_team_id=team2.id,
        home_score=2,
        away_score=1
    )
    
    # Fixture in the future (not started)
    future_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    fixture2 = Fixture(
        api_fixture_id=102,
        api_league_id=1,
        api_season=2026,
        api_round='GROUP_STAGE',
        start_at=future_time,
        home_team_id=team2.id,
        away_team_id=team3.id,
        home_score=None,
        away_score=None
    )
    
    # Another future fixture
    future_time2 = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
    fixture3 = Fixture(
        api_fixture_id=103,
        api_league_id=1,
        api_season=2026,
        api_round='QUARTER_FINALS',
        start_at=future_time2,
        home_team_id=team1.id,
        away_team_id=team3.id,
        home_score=None,
        away_score=None
    )
    
    db.session.add_all([fixture1, fixture2, fixture3])
    db.session.commit()
    return [fixture1, fixture2, fixture3]


@pytest.fixture
def predictions(db, admin_user, regular_user, fixtures):
    """Create and return sample predictions."""
    fixture1, fixture2, fixture3 = fixtures
    
    # Admin user predictions
    pred1 = Prediction(user_id=admin_user.id, fixture_id=fixture1.id, score1=2, score2=1)
    pred2 = Prediction(user_id=admin_user.id, fixture_id=fixture2.id, score1=1, score2=0)
    
    # Regular user predictions
    pred3 = Prediction(user_id=regular_user.id, fixture_id=fixture1.id, score1=1, score2=1)
    pred4 = Prediction(user_id=regular_user.id, fixture_id=fixture2.id, score1=3, score2=2)
    
    db.session.add_all([pred1, pred2, pred3, pred4])
    db.session.commit()
    return [pred1, pred2, pred3, pred4]
