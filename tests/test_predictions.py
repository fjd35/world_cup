"""Tests for prediction routes."""

import pytest
from src.models import Prediction


class TestAddPrediction:
    """Test add/update prediction route."""
    
    def test_add_prediction_not_logged_in(self, client, fixtures):
        """Test adding prediction without being logged in."""
        fixture = fixtures[1]  # Future fixture
        response = client.post('/add_prediction', data={
            'fixture_id': fixture.id,
            'score1': 2,
            'score2': 1
        })
        
        assert response.status_code == 302  # Redirect to login
    
    def test_add_prediction_valid(self, client, db, admin_user, fixtures):
        """Test adding a valid prediction."""
        fixture = fixtures[1]  # Future fixture (not started)
        
        # Login
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        # Add prediction
        response = client.post('/add_prediction', data={
            'fixture_id': fixture.id,
            'score1': 2,
            'score2': 1
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check prediction was created
        prediction = db.session.query(Prediction).filter_by(
            user_id=admin_user.id,
            fixture_id=fixture.id
        ).first()
        assert prediction is not None
        assert prediction.score1 == 2
        assert prediction.score2 == 1
    
    def test_update_prediction(self, client, db, admin_user, fixtures, predictions):
        """Test updating an existing prediction."""
        fixture = fixtures[1]  # Future fixture
        
        # Login
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        # Update prediction
        response = client.post('/add_prediction', data={
            'fixture_id': fixture.id,
            'score1': 3,
            'score2': 2
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check prediction was updated
        prediction = db.session.query(Prediction).filter_by(
            user_id=admin_user.id,
            fixture_id=fixture.id
        ).first()
        assert prediction is not None
        assert prediction.score1 == 3
        assert prediction.score2 == 2
    
    def test_add_prediction_fixture_not_found(self, client, admin_user):
        """Test adding prediction for non-existent fixture."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/add_prediction', data={
            'fixture_id': 99999,
            'score1': 2,
            'score2': 1
        })
        
        assert response.status_code == 404
    
    def test_add_prediction_already_started_fixture(self, client, admin_user, fixtures):
        """Test adding prediction for fixture that has already started."""
        fixture = fixtures[0]  # Past fixture (started)
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/add_prediction', data={
            'fixture_id': fixture.id,
            'score1': 2,
            'score2': 1
        })
        
        assert response.status_code == 400
    
    def test_add_prediction_missing_teams(self, client, db, admin_user, teams):
        """Test adding prediction for fixture without teams."""
        from src.models import Fixture
        from datetime import datetime, timezone, timedelta
        
        future_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        fixture = Fixture(
            api_fixture_id=999,
            start_at=future_time,
            home_team_id=None,  # Missing home team
            away_team_id=None   # Missing away team
        )
        db.session.add(fixture)
        db.session.commit()
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/add_prediction', data={
            'fixture_id': fixture.id,
            'score1': 2,
            'score2': 1
        })
        
        assert response.status_code == 400


class TestMyPredictions:
    """Test my_predictions route."""
    
    def test_my_predictions_not_logged_in(self, client):
        """Test accessing my_predictions without being logged in."""
        response = client.get('/my_predictions')
        assert response.status_code == 302  # Redirect to login
    
    def test_my_predictions_logged_in(self, client, admin_user, fixtures):
        """Test accessing my_predictions when logged in."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.get('/my_predictions')
        assert response.status_code == 200
        assert b'predictions' in response.data.lower()
    
    def test_my_predictions_shows_fixtures(self, client, admin_user, fixtures, predictions):
        """Test that my_predictions page shows fixtures."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.get('/my_predictions')
        assert response.status_code == 200
        # Should show team names
        assert b'England' in response.data or b'France' in response.data
    
    def test_my_predictions_empty(self, client, regular_user, fixtures):
        """Test my_predictions page for user with no predictions."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password456'
        })
        
        response = client.get('/my_predictions')
        assert response.status_code == 200
