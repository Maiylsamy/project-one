# Project One — Secure FastAPI Authentication API

> Production-ready REST API with JWT authentication, PostgreSQL, 
> Docker deployment, and 94% test coverage.

---

## Live Demo

| Resource | URL |
|---|---|
| API Base | https://your-render-url.onrender.com |
| Health Check | https://your-render-url.onrender.com/health |

> Swagger UI disabled in production (security best practice).
> Request API documentation via email.

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.12 |
| Framework | FastAPI | Latest |
| Database | PostgreSQL (Supabase) | 16 |
| ORM | SQLAlchemy + Alembic | Latest |
| Auth | JWT (python-jose) | Latest |
| Password Hashing | pwdlib + argon2 | Latest |
| Rate Limiting | slowapi | Latest |
| Security Headers | secure | 2.0.1 |
| Containerization | Docker | 29.x |
| Hosting | Render (Free tier) | — |
| CI/CD | GitHub Actions | — |
| Testing | pytest | 9.x |

---

## Security Features

| Feature | Implementation |
|---|---|
| Password hashing | argon2 via pwdlib (industry standard) |
| Auth tokens | JWT with 30-minute expiry |
| Brute force protection | Rate limiting — 5 login attempts/minute per IP |
| Registration protection | Rate limiting — 3 registrations/hour per IP |
| CORS | Whitelist only — no wildcard |
| Security headers | HSTS, X-Frame-Options, CSP, Referrer-Policy |
| Input validation | Pydantic validators on all endpoints |
| Error handling | Generic errors — no stack traces exposed |
| Swagger in production | Disabled (returns 404) |
| Dependency scanning | pip-audit in CI pipeline |
| Static analysis | bandit in CI pipeline |

---

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /health | No | Server + DB health check |
| POST | /auth/register | No | Create new account |
| POST | /auth/login | No | Get JWT access token |
| GET | /users/me | Yes (Bearer) | Get current user profile |

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Docker Desktop
- PostgreSQL (or Supabase free tier)

### Setup

```bash
# Clone repository
git clone https://github.com/Maiylsamy/project-one.git
cd project-one

# Install dependencies
pip install poetry
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your database URL and secret key

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload

# API available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Run with Docker

```bash
docker build -t project-one .
docker run -p 8000:8000 --env-file .env project-one
```

---

## Project Structure
project-one/
├── app/
│ ├── core/
│ │ ├── config.py # Environment variable loading
│ │ ├── security.py # Password hashing + JWT
│ │ ├── deps.py # Auth dependency (route guard)
│ │ ├── limiter.py # Rate limiting config
│ │ └── errors.py # Global error handlers
│ ├── db/
│ │ └── database.py # SQLAlchemy engine + session
│ ├── models/
│ │ └── user.py # Database table definition
│ ├── schemas/
│ │ ├── user.py # Request/response shapes
│ │ └── auth.py # Token + login schemas
│ ├── services/
│ │ └── user_service.py # Business logic layer
│ ├── routers/
│ │ ├── auth.py # /auth endpoints
│ │ └── users.py # /users endpoints
│ └── main.py # FastAPI app entry point
├── tests/
│ ├── conftest.py # Test fixtures + DB override
│ ├── test_auth.py # Auth endpoint tests
│ ├── test_users.py # Protected route tests
│ └── test_security.py # Security-specific tests
├── alembic/ # Database migrations
├── Dockerfile # Container definition
├── docker-compose.yml # Local dev setup
└── pyproject.toml # Dependencies

---

## Test Coverage
32 tests passing
94% code coverage
Security scan: clean (bandit)
Dependency audit: clean (pip-audit)
CI/CD: GitHub Actions (auto-runs on every push)

---

## Environment Variables

```bash
# Copy template
cp .env.example .env
```

| Variable | Description | Example |
|---|---|---|
| DATABASE_URL | PostgreSQL connection string | postgresql://user:pass@host:5432/db |
| SECRET_KEY | JWT signing key (min 32 chars) | Generate with: python -c "import secrets; print(secrets.token_hex(32))" |
| DEBUG | Show Swagger UI (dev only) | True / False |
| ALLOWED_ORIGINS | CORS whitelist | http://localhost:3000 |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT expiry | 30 |

---

## Deployment

This project is deployed on Render using Docker.
Push to main branch
→ GitHub Actions runs tests + security scan
→ All pass → Render auto-deploys
→ Zero downtime deployment

---

## Author

**Maiylsamy Durai**
Associate Software Engineer | Python Backend Developer
[GitHub](https://github.com/Maiylsamy) | [LinkedIn](https://linkedin.com/in/maiylsamy)
