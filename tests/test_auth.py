# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient


class TestRegister:
    """Tests for POST /auth/register"""

    def test_register_success(self, client, fake_user_data):
        # Happy path — valid email + strong password
        res = client.post("/auth/register", json=fake_user_data)
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == fake_user_data["email"]
        assert "id" in data
        assert "is_active" in data
        assert data["is_active"] is True

    def test_register_password_never_in_response(self, client, fake_user_data):
        # Security: raw or hashed password must NEVER appear in response
        res = client.post("/auth/register", json=fake_user_data)
        body = str(res.json())
        assert "password" not in body
        assert "hashed_password" not in body
        assert fake_user_data["password"] not in body

    def test_register_duplicate_email(self, client, fake_user_data):
        # Same email twice = 400 error
        client.post("/auth/register", json=fake_user_data)
        res = client.post("/auth/register", json=fake_user_data)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"].lower()

    def test_register_invalid_email_format(self, client):
        # Pydantic EmailStr rejects non-email strings
        res = client.post("/auth/register", json={
            "email": "notanemail",
            "password": "Test1234"
        })
        assert res.status_code == 422

    def test_register_password_too_short(self, client):
        # Validator rejects passwords under 8 chars
        res = client.post("/auth/register", json={
            "email": "test@test.com",
            "password": "Ab1"
        })
        assert res.status_code == 422

    def test_register_password_no_uppercase(self, client):
        # Validator requires at least one uppercase letter
        res = client.post("/auth/register", json={
            "email": "test@test.com",
            "password": "test1234"
        })
        assert res.status_code == 422

    def test_register_password_no_number(self, client):
        # Validator requires at least one number
        res = client.post("/auth/register", json={
            "email": "test@test.com",
            "password": "TestPass"
        })
        assert res.status_code == 422

    def test_register_missing_email(self, client):
        # Missing required field = 422
        res = client.post("/auth/register", json={"password": "Test1234"})
        assert res.status_code == 422

    def test_register_missing_password(self, client):
        # Missing required field = 422
        res = client.post("/auth/register", json={"email": "test@test.com"})
        assert res.status_code == 422

    def test_register_empty_body(self, client):
        # Empty request body = 422
        res = client.post("/auth/register", json={})
        assert res.status_code == 422


class TestLogin:
    """Tests for POST /auth/login"""

    def test_login_success(self, client, fake_user_data):
        # Happy path — correct credentials returns token
        client.post("/auth/register", json=fake_user_data)
        res = client.post("/auth/login", json=fake_user_data)
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20  # real token, not empty string

    def test_login_wrong_password(self, client, fake_user_data):
        # Wrong password = 401
        client.post("/auth/register", json=fake_user_data)
        res = client.post("/auth/login", json={
            "email": fake_user_data["email"],
            "password": "WrongPass99"
        })
        assert res.status_code == 401

    def test_login_wrong_email(self, client):
        # Non-existent email = 401 (same error as wrong password)
        res = client.post("/auth/login", json={
            "email": "ghost@nowhere.com",
            "password": "Test1234"
        })
        assert res.status_code == 401

    def test_login_error_message_identical_for_wrong_email_and_password(
        self, client, fake_user_data
    ):
        # Security: error message must be IDENTICAL for both cases
        # Prevents attacker from knowing which field is wrong (email enumeration)
        client.post("/auth/register", json=fake_user_data)

        wrong_pass = client.post("/auth/login", json={
            "email": fake_user_data["email"],
            "password": "WrongPass99"
        })
        wrong_email = client.post("/auth/login", json={
            "email": "nobody@nowhere.com",
            "password": fake_user_data["password"]
        })
        # Same message for both — attacker learns nothing
        assert wrong_pass.json()["detail"] == wrong_email.json()["detail"]

    def test_login_missing_fields(self, client):
        # Empty body = 422
        res = client.post("/auth/login", json={})
        assert res.status_code == 422