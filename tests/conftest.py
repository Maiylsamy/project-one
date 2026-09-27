# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db

# ── Test Database ────────────────────────────────────────────
# SQLite in-memory = fast, isolated, no cleanup needed
# Each test gets fresh tables — no leftover data between tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    # StaticPool = single connection shared across test session
    # Required for SQLite in-memory (multiple connections = separate DBs)
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ── Override FastAPI's DB dependency ─────────────────────────
# Replaces real PostgreSQL with test SQLite for all routes
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_db():
    # Creates all tables before EACH test
    Base.metadata.create_all(bind=engine)
    yield
    # Drops all tables after EACH test = clean slate every time
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    # TestClient = makes HTTP requests to your app without running a real server
    with TestClient(app) as c:
        yield c

@pytest.fixture
def fake_user_data():
    # Faker generates unique random test data — avoids hardcoded emails
    from faker import Faker
    fake = Faker()
    return {
        "email": fake.email(),
        "password": "Test1234"
    }

@pytest.fixture
def registered_user(client, fake_user_data):
    # Reusable fixture — registers + logs in a user, returns everything needed
    # Used by any test that needs an authenticated user without repeating steps

    # Register
    res = client.post("/auth/register", json=fake_user_data)
    assert res.status_code == 201

    # Login to get token
    login_res = client.post("/auth/login", json=fake_user_data)
    token = login_res.json()["access_token"]

    return {
        "user": res.json(),
        "token": token,
        "email": fake_user_data["email"],
        "password": fake_user_data["password"],
        # Pre-built auth header — pass directly to any protected request
        "headers": {"Authorization": f"Bearer {token}"}
    }