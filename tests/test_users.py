# tests/test_users.py
import pytest
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings


class TestGetMe:
    """Tests for GET /users/me"""

    def test_get_me_success(self, client, registered_user):
        # Valid token = returns current user's data
        res = client.get("/users/me", headers=registered_user["headers"])
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == registered_user["email"]
        assert data["is_active"] is True

    def test_get_me_password_not_in_response(self, client, registered_user):
        # Security: password must never appear in /users/me response
        res = client.get("/users/me", headers=registered_user["headers"])
        body = str(res.json())
        assert "password" not in body
        assert "hashed_password" not in body

    def test_get_me_no_token(self, client):
        # No Authorization header = 401
        res = client.get("/users/me")
        assert res.status_code == 401

    def test_get_me_invalid_token(self, client):
        # Garbage token = 401
        res = client.get("/users/me", headers={
            "Authorization": "Bearer faketoken.fake.fake"
        })
        assert res.status_code == 401

    def test_get_me_malformed_header(self, client):
        # Missing "Bearer " prefix = 401
        res = client.get("/users/me", headers={
            "Authorization": "NotBearer sometoken"
        })
        assert res.status_code == 401

    def test_get_me_expired_token(self, client, fake_user_data):
        # Manually craft an already-expired token
        # exp set to 1 hour in the PAST = expired
        expired_token = jwt.encode(
            {
                "sub": "1",
                "exp": datetime.utcnow() - timedelta(hours=1)
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        res = client.get("/users/me", headers={
            "Authorization": f"Bearer {expired_token}"
        })
        assert res.status_code == 401

    def test_get_me_token_with_nonexistent_user(self, client):
        # Valid token structure but user_id doesn't exist in DB
        # Happens when user is deleted after token was issued
        token = jwt.encode(
            {
                "sub": "99999",  # user_id that doesn't exist
                "exp": datetime.utcnow() + timedelta(hours=1)
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        res = client.get("/users/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert res.status_code == 401