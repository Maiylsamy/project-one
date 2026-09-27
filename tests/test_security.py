# tests/test_security.py
import json
import pytest


class TestSecurityHeaders:
    """Verify security headers present on every response"""

    def test_security_headers_present(self, client):
        # All responses must include these headers (added by secure middleware)
        res = client.get("/health")
        headers = res.headers
        assert "x-frame-options" in headers        # clickjacking protection
        assert "x-content-type-options" in headers # MIME sniffing protection
        assert "strict-transport-security" in headers  # force HTTPS


class TestInputValidation:
    """Verify malicious inputs are safely rejected"""

    def test_sql_injection_in_login(self, client):
        # Classic SQL injection attempt in email field
        # Should return 401 or 422 — never 200 or 500
        res = client.post("/auth/login", json={
            "email": "' OR '1'='1'; --",
            "password": "anything"
        })
        assert res.status_code in [401, 422]

    def test_xss_payload_in_register(self, client):
        # XSS script tag in email = rejected by EmailStr validator
        res = client.post("/auth/register", json={
            "email": "<script>alert('xss')</script>@evil.com",
            "password": "Test1234"
        })
        assert res.status_code == 422

    def test_extremely_long_email_rejected(self, client):
        # Oversized input attempt — should not crash server
        res = client.post("/auth/login", json={
            "email": "a" * 10000 + "@test.com",
            "password": "b" * 10000
        })
        assert res.status_code in [401, 422]

    def test_null_bytes_in_input(self, client):
        # Null byte injection attempt
        res = client.post("/auth/login", json={
            "email": "test\x00@test.com",
            "password": "Test1234"
        })
        assert res.status_code in [401, 422]


class TestPasswordSecurity:
    """Verify password never leaks in any response"""

    def test_password_not_in_register_response(self, client):
        res = client.post("/auth/register", json={
            "email": "leak@test.com",
            "password": "Test1234"
        })
        body = json.dumps(res.json())
        assert "Test1234" not in body
        assert "hashed_password" not in body

    def test_password_not_in_login_response(self, client):
        # Register first
        client.post("/auth/register", json={
            "email": "leak2@test.com",
            "password": "Test1234"
        })
        # Login response should only have token, never password
        res = client.post("/auth/login", json={
            "email": "leak2@test.com",
            "password": "Test1234"
        })
        body = json.dumps(res.json())
        assert "Test1234" not in body
        assert "hashed_password" not in body


class TestPublicEndpoints:
    """Verify endpoints that must be publicly accessible"""

    def test_health_endpoint_no_auth_required(self, client):
        # /health must work without any token — used by monitoring tools
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_register_no_auth_required(self, client):
        # New users can't register if auth is required (chicken-and-egg)
        res = client.post("/auth/register", json={
            "email": "public@test.com",
            "password": "Test1234"
        })
        assert res.status_code == 201

    def test_login_no_auth_required(self, client):
        # Login endpoint must be publicly accessible
        client.post("/auth/register", json={
            "email": "public2@test.com",
            "password": "Test1234"
        })
        res = client.post("/auth/login", json={
            "email": "public2@test.com",
            "password": "Test1234"
        })
        assert res.status_code == 200