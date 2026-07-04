"""Tests for admin routes."""

import pytest
from src.models import Fixture, User, Prediction


class TestAdminAccess:
    """Test admin route access control."""
    
    def test_admin_not_logged_in(self, client):
        """Test accessing admin without being logged in."""
        response = client.get('/admin')
        assert response.status_code == 302  # Redirect to login
    
    def test_admin_non_admin_user(self, client, regular_user):
        """Test accessing admin as non-admin user."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password456'
        })
        
        response = client.get('/admin')
        assert response.status_code == 403  # Forbidden
    
    def test_admin_admin_user(self, client, admin_user, fixtures):
        """Test accessing admin as admin user."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.get('/admin')
        assert response.status_code == 200
        assert b'admin' in response.data.lower()


class TestUpdateFixture:
    """Test update_fixture route."""
    
    def test_update_fixture_not_admin(self, client, regular_user, fixtures):
        """Test updating fixture as non-admin user."""
        fixture = fixtures[0]
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password456'
        })
        
        response = client.post('/update_fixture', data={
            'fixture_id': fixture.id,
            'home_score': 3,
            'away_score': 2
        })
        
        assert response.status_code == 403
    
    def test_update_fixture_valid(self, client, db, admin_user, fixtures):
        """Test updating fixture scores as admin."""
        fixture = fixtures[1]  # Future fixture
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/update_fixture', data={
            'fixture_id': fixture.id,
            'home_score': 2,
            'away_score': 1
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check fixture was updated
        updated = db.session.get(Fixture, fixture.id)
        assert updated.home_score == 2
        assert updated.away_score == 1
    
    def test_update_fixture_empty_scores(self, client, db, admin_user, fixtures):
        """Test updating fixture with empty scores."""
        fixture = fixtures[1]
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/update_fixture', data={
            'fixture_id': fixture.id,
            'home_score': '',
            'away_score': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check scores are None
        updated = db.session.get(Fixture, fixture.id)
        assert updated.home_score is None
        assert updated.away_score is None


class TestUpdateScores:
    """Test update_scores route."""
    
    def test_update_scores_not_admin(self, client, regular_user):
        """Test updating scores as non-admin user."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password456'
        })
        
        response = client.get('/update_scores')
        assert response.status_code == 403
    
    def test_update_scores_admin(self, client, admin_user, fixtures, predictions):
        """Test updating scores as admin."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.get('/update_scores', follow_redirects=True)
        assert response.status_code == 200
    
    def test_update_scores_calculates_correctly(self, client, db, admin_user, fixtures, predictions):
        """Test that update_scores calculates user scores correctly."""
        # fixtures[0] has home_score=2, away_score=1
        # admin_user predicted 2-1 (exact match = 3 points)
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        client.get('/update_scores', follow_redirects=True)
        
        # Refresh user from db
        updated_user = db.session.get(User, admin_user.id)
        assert updated_user.score >= 3  # At least 3 points for the exact match


class TestDeleteUser:
    """Test delete_user route."""
    
    def test_delete_user_not_admin(self, client, regular_user, admin_user):
        """Test deleting user as non-admin."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password456'
        })
        
        response = client.post('/admin/delete_user', data={
            'user_id': admin_user.id
        })
        
        assert response.status_code == 403
    
    def test_delete_user_admin_cannot_delete_self(self, client, admin_user):
        """Test that admin user (id=1) cannot be deleted."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/admin/delete_user', data={
            'user_id': 1
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'cannot delete the admin user' in response.data.lower()
    
    def test_delete_user_valid(self, client, db, admin_user, regular_user, predictions):
        """Test deleting a regular user."""
        user_id = regular_user.id
        user_predictions = db.session.query(Prediction).filter_by(user_id=user_id).all()
        prediction_count = len(user_predictions)
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/admin/delete_user', data={
            'user_id': user_id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check user and predictions are deleted
        deleted_user = db.session.get(User, user_id)
        assert deleted_user is None
        
        remaining_predictions = db.session.query(Prediction).filter_by(user_id=user_id).all()
        assert len(remaining_predictions) == 0
    
    def test_delete_user_not_found(self, client, admin_user):
        """Test deleting non-existent user."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/admin/delete_user', data={
            'user_id': 99999
        })
        
        assert response.status_code == 404


        class TestUpdateUserId:
            """Test update_user_id route."""

            def test_update_user_id_not_admin(self, client, regular_user):
                """Test changing a user id as a non-admin."""
                client.post('/login', data={
                    'username': 'testuser',
                    'password': 'password456'
                })

                response = client.post('/admin/update_user_id', data={
                    'current_user_id': regular_user.id,
                    'new_user_id': 5,
                })

                assert response.status_code == 403

            def test_update_user_id_valid(self, client, db, admin_user, regular_user, predictions):
                """Test updating a user's id also rewrites their predictions."""
                old_user_id = regular_user.id
                new_user_id = 5

                client.post('/login', data={
                    'username': 'admin',
                    'password': 'password123'
                })

                response = client.post('/admin/update_user_id', data={
                    'current_user_id': old_user_id,
                    'new_user_id': new_user_id,
                }, follow_redirects=True)

                assert response.status_code == 200
                assert b'updated user testuser from id 2 to 5' in response.data.lower()

                updated_user = db.session.get(User, new_user_id)
                assert updated_user is not None
                assert updated_user.username == 'testuser'
                assert db.session.get(User, old_user_id) is None

                updated_predictions = db.session.query(Prediction).filter_by(user_id=new_user_id).all()
                assert len(updated_predictions) == 2
                assert db.session.query(Prediction).filter_by(user_id=old_user_id).count() == 0

            def test_update_user_id_rejects_duplicate(self, client, db, admin_user, regular_user):
                """Test that a user id cannot be changed to an existing id."""
                client.post('/login', data={
                    'username': 'admin',
                    'password': 'password123'
                })

                response = client.post('/admin/update_user_id', data={
                    'current_user_id': regular_user.id,
                    'new_user_id': admin_user.id,
                }, follow_redirects=True)

                assert response.status_code == 200
                assert b'already in use' in response.data.lower()

            def test_update_user_id_admin_protected(self, client, admin_user):
                """Test that the admin id itself cannot be changed."""
                client.post('/login', data={
                    'username': 'admin',
                    'password': 'password123'
                })

                response = client.post('/admin/update_user_id', data={
                    'current_user_id': admin_user.id,
                    'new_user_id': 3,
                }, follow_redirects=True)

                assert response.status_code == 200
                assert b'cannot change the admin user' in response.data.lower()


class TestIndex:
    """Test index route."""
    
    def test_index_page(self, client):
        """Test index page loads."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_shows_users(self, client, admin_user, regular_user):
        """Test index page shows users sorted by score."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'admin' in response.data.lower() or b'testuser' in response.data.lower()


class TestAccountRoutes:
    """Test account management routes."""
    
    def test_account_page_not_logged_in(self, client):
        """Test accessing account without login."""
        response = client.get('/account')
        assert response.status_code == 302  # Redirect
    
    def test_account_page_logged_in(self, client, admin_user):
        """Test accessing account when logged in."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.get('/account')
        assert response.status_code == 200
    
    def test_update_account_invalid_password(self, client, admin_user):
        """Test updating account with wrong current password."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/account', data={
            'current_password': 'wrongpassword',
            'username': 'admin',
            'new_password': '',
            'confirm_password': ''
        }, follow_redirects=True)
        
        assert b'incorrect' in response.data.lower()
    
    def test_update_account_username(self, client, db, admin_user):
        """Test updating username."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/account', data={
            'current_password': 'password123',
            'username': 'newadmin',
            'new_password': '',
            'confirm_password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check username was updated
        updated = db.session.get(User, admin_user.id)
        assert updated.username == 'newadmin'
    
    def test_update_account_password(self, client, db, admin_user):
        """Test updating password."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/account', data={
            'current_password': 'password123',
            'username': 'admin',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestDeleteAccount:
    """Test account deletion."""
    
    def test_delete_account_not_logged_in(self, client):
        """Test deleting account without login."""
        response = client.post('/account/delete')
        assert response.status_code == 302  # Redirect
    
    def test_delete_account_wrong_password(self, client, admin_user):
        """Test deleting account with wrong password."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        response = client.post('/account/delete', data={
            'current_password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'required and must be correct' in response.data.lower()
    
    def test_delete_account_valid(self, client, db, regular_user, predictions):
        """Test valid account deletion."""
        user_id = regular_user.id
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password456'
        })
        
        response = client.post('/account/delete', data={
            'current_password': 'password456'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check user is deleted
        deleted_user = db.session.get(User, user_id)
        assert deleted_user is None
