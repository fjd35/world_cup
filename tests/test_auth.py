"""Tests for authentication routes."""

import pytest
from werkzeug.security import check_password_hash
from src.models import User


class TestSignup:
    """Test signup route."""
    
    def test_signup_page_get(self, client):
        """Test GET signup page."""
        response = client.get('/signup')
        assert response.status_code == 200
        assert b'signup' in response.data.lower() or b'sign up' in response.data.lower()
    
    def test_signup_valid(self, client, db):
        """Test valid signup."""
        response = client.post('/signup', data={
            'key': '3lions',
            'username': 'newuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        user = db.session.query(User).filter_by(username='newuser').first()
        assert user is not None
        assert user.username == 'newuser'
        assert check_password_hash(user.password, 'password123')
    
    def test_signup_missing_fields(self, client, db):
        """Test signup with missing fields."""
        response = client.post('/signup', data={
            'key': '3lions',
            'username': '',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'fill in all fields' in response.data.lower()
        user = db.session.query(User).filter_by(username='').first()
        assert user is None
    
    def test_signup_invalid_invitation_key(self, client, db):
        """Test signup with invalid invitation key."""
        response = client.post('/signup', data={
            'key': 'wrongkey',
            'username': 'newuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'invitation key incorrect' in response.data.lower()
        user = db.session.query(User).filter_by(username='newuser').first()
        assert user is None
    
    def test_signup_duplicate_username(self, client, db, admin_user):
        """Test signup with existing username."""
        response = client.post('/signup', data={
            'key': '3lions',
            'username': 'admin',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'username already exists' in response.data.lower()
    
    def test_signup_valid_invitation_keys(self, client, db):
        """Test all valid invitation keys work."""
        for key in ['3lions', 'wc26']:
            response = client.post('/signup', data={
                'key': key,
                'username': f'user_{key}',
                'password': 'password123'
            }, follow_redirects=True)
            
            user = db.session.query(User).filter_by(username=f'user_{key}').first()
            assert user is not None


class TestLogin:
    """Test login route."""
    
    def test_login_page_get(self, client):
        """Test GET login page."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_login_valid(self, client, admin_user):
        """Test valid login."""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'admin' in response.data.lower()
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'check your login details' in response.data.lower()
    
    def test_login_invalid_password(self, client, admin_user):
        """Test login with wrong password."""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'check your login details' in response.data.lower()
    
    def test_login_remember_me(self, client, admin_user):
        """Test login with remember me checkbox."""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'password123',
            'remember': 'on'
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestLogout:
    """Test logout route."""
    
    def test_logout(self, client, admin_user):
        """Test logout."""
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        # Should be redirected to index


class TestLogoutRedirect:
    """Test logout redirect without login."""
    
    def test_logout_redirect_when_not_logged_in(self, client):
        """Test logout redirect when not logged in."""
        response = client.get('/logout')
        # Should redirect to login
        assert response.status_code == 302 or response.status_code == 401
