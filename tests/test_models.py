"""Tests for database models."""

import pytest
from datetime import datetime, timezone, timedelta
from src.models import User, Team, Fixture, Prediction


class TestUser:
    """Test User model."""
    
    def test_user_creation(self, db):
        """Test creating a user."""
        user = User(username='testuser', password='hashedpass123')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.password == 'hashedpass123'
        assert user.score == 0
    
    def test_user_repr(self, admin_user):
        """Test user string representation."""
        repr_str = repr(admin_user)
        assert 'User' in repr_str
        assert 'admin' in repr_str
    
    def test_user_unique_username(self, db, admin_user):
        """Test that usernames must be unique."""
        duplicate_user = User(username='admin', password='differentpass')
        db.session.add(duplicate_user)
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db.session.commit()
    
    def test_user_predictions_relationship(self, db, admin_user, fixtures, predictions):
        """Test user-predictions relationship."""
        user = db.session.get(User, admin_user.id)
        assert len(user.predictions) == 2
        assert all(isinstance(p, Prediction) for p in user.predictions)


class TestTeam:
    """Test Team model."""
    
    def test_team_creation(self, db):
        """Test creating a team."""
        team = Team(name='England', tla='ENG', api_team_id=1, crest_url='http://example.com/eng.png')
        db.session.add(team)
        db.session.commit()
        
        assert team.id is not None
        assert team.name == 'England'
        assert team.tla == 'ENG'
        assert team.api_team_id == 1
    
    def test_team_repr(self, teams):
        """Test team string representation."""
        team = teams[0]
        repr_str = repr(team)
        assert 'Team' in repr_str
        assert 'England' in repr_str
    
    def test_team_unique_name(self, db, teams):
        """Test that team names must be unique."""
        duplicate_team = Team(name='England', tla='ENG2')
        db.session.add(duplicate_team)
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db.session.commit()
    
    def test_team_relationships(self, db, fixtures, teams):
        """Test team fixtures relationships."""
        team = db.session.get(Team, teams[0].id)
        assert len(team.home_fixtures) >= 1
        assert len(team.away_fixtures) >= 0


class TestFixture:
    """Test Fixture model."""
    
    def test_fixture_creation(self, db, teams):
        """Test creating a fixture."""
        team1, team2, _ = teams
        fixture = Fixture(
            api_fixture_id=1,
            api_league_id=1,
            api_season=2026,
            api_round='GROUP_STAGE',
            start_at='2026-06-15T14:00:00Z',
            home_team_id=team1.id,
            away_team_id=team2.id,
            home_score=None,
            away_score=None
        )
        db.session.add(fixture)
        db.session.commit()
        
        assert fixture.id is not None
        assert fixture.api_fixture_id == 1
        assert fixture.api_season == 2026
    
    def test_fixture_repr(self, fixtures):
        """Test fixture string representation."""
        fixture = fixtures[0]
        repr_str = repr(fixture)
        assert 'Fixture' in repr_str
        assert 'England' in repr_str
        assert 'France' in repr_str
    
    def test_fixture_team_names(self, fixtures):
        """Test fixture team name properties."""
        fixture = fixtures[0]
        assert fixture.home_team_name == 'England'
        assert fixture.away_team_name == 'France'
    
    def test_fixture_has_started_past(self, fixtures):
        """Test has_started property for past fixture."""
        fixture = fixtures[0]  # Created in the past
        assert fixture.has_started is True
    
    def test_fixture_has_started_future(self, fixtures):
        """Test has_started property for future fixture."""
        fixture = fixtures[1]  # Created in the future
        assert fixture.has_started is False
    
    def test_fixture_has_started_no_start_at(self, db, teams):
        """Test has_started when start_at is None."""
        team1, team2, _ = teams
        fixture = Fixture(
            home_team_id=team1.id,
            away_team_id=team2.id,
            start_at=None
        )
        db.session.add(fixture)
        db.session.commit()
        
        assert fixture.has_started is False
    
    def test_fixture_has_started_invalid_format(self, db, teams):
        """Test has_started with invalid date format."""
        team1, team2, _ = teams
        fixture = Fixture(
            home_team_id=team1.id,
            away_team_id=team2.id,
            start_at='invalid-date-format'
        )
        db.session.add(fixture)
        db.session.commit()
        
        assert fixture.has_started is False


class TestPrediction:
    """Test Prediction model."""
    
    def test_prediction_creation(self, db, admin_user, fixtures):
        """Test creating a prediction."""
        fixture = fixtures[0]
        prediction = Prediction(
            user_id=admin_user.id,
            fixture_id=fixture.id,
            score1=2,
            score2=1
        )
        db.session.add(prediction)
        db.session.commit()
        
        assert prediction.id is not None
        assert prediction.score1 == 2
        assert prediction.score2 == 1
    
    def test_prediction_repr(self, predictions):
        """Test prediction string representation."""
        prediction = predictions[0]
        repr_str = repr(prediction)
        assert 'Prediction' in repr_str
        assert 'admin' in repr_str or 'England' in repr_str
    
    def test_prediction_user_relationship(self, db, predictions, admin_user):
        """Test prediction-user relationship."""
        prediction = db.session.get(Prediction, predictions[0].id)
        assert prediction.user.username == 'admin'
    
    def test_prediction_fixture_relationship(self, db, predictions, fixtures):
        """Test prediction-fixture relationship."""
        prediction = db.session.get(Prediction, predictions[0].id)
        assert prediction.fixture.id == fixtures[0].id


class TestModelIntegrity:
    """Test model relationships and integrity."""
    
    def test_delete_user_cascades_predictions(self, db, regular_user, predictions):
        """Test that deleting a user deletes their predictions."""
        user_id = int(regular_user.id)
        predictions_count = len(db.session.query(Prediction).filter_by(user_id=user_id).all())
        assert predictions_count > 0
        
        db.session.delete(regular_user)
        db.session.commit()
        
        remaining = db.session.query(Prediction).filter_by(user_id=user_id).all()
        assert len(remaining) == 0
    
    def test_fixture_with_teams(self, db, teams):
        """Test fixture maintains proper team relationships."""
        team1, team2, _ = teams
        fixture = Fixture(
            home_team_id=team1.id,
            away_team_id=team2.id,
            home_score=2,
            away_score=1
        )
        db.session.add(fixture)
        db.session.commit()
        
        fetched = db.session.get(Fixture, fixture.id)
        assert fetched.home_team.name == 'England'
        assert fetched.away_team.name == 'France'
