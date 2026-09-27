# Project Handoff Document
**Project:** Secure FastAPI Authentication API
**Developer:** Maiylsamy Durai
**Delivered:** September 2026

---

## What Was Built

A production-ready REST API providing secure user authentication.
Handles registration, login, JWT token issuance, and protected
route access. Built to be extended as a foundation for any
SaaS, mobile app, or web application backend.

---

## Live Environment

| Resource | Value |
|---|---|
| API URL | https://your-render-url.onrender.com |
| Health Check | https://your-render-url.onrender.com/health |
| Database | Supabase PostgreSQL (free tier) |
| Hosting | Render (free tier) |

---

## How to Redeploy

```bash
# Any push to main branch triggers auto-deployment
git push origin main

# Monitor deployment:
# Render Dashboard → your service → Logs tab
```

---

## How to Run Migrations (Schema Changes)

```bash
# After editing app/models/user.py:
poetry run alembic revision --autogenerate -m "description of change"
poetry run alembic upgrade head
```

---

## How to Rollback a Migration

```bash
poetry run alembic downgrade -1
```

---

## Environment Variables Location
Render Dashboard → your service → Environment tab
→ All production secrets stored here
→ Never in code or committed files

---

## Test Suite

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=app --cov-report=term-missing
```

Current status: 32 tests, 94% coverage.

---

## Security Measures in Place

1. Passwords hashed with argon2 — irreversible, salted
2. JWT tokens expire after 30 minutes
3. Login rate limited — 5 attempts/minute per IP
4. Registration rate limited — 3/hour per IP
5. CORS restricted to whitelisted origins only
6. Security headers on every response (HSTS, CSP, X-Frame-Options)
7. No stack traces exposed to clients
8. Swagger docs hidden in production
9. Dependency CVE scanning in CI pipeline
10. Static security analysis (bandit) in CI pipeline

---

## Known Limitations (Free Tier)

| Limitation | Impact | Resolution |
|---|---|---|
| Render free tier sleeps after 15min inactivity | 30-60s cold start on first request | Upgrade to $7/mo Starter plan |
| Supabase pauses after 7 days inactivity | DB connection fails until resumed | Set up keep-alive ping or upgrade |
| No SSH access on Render free tier | Can't terminal into server | Use Render logs for debugging |

---

## Monitoring

UptimeRobot monitors /health endpoint every 5 minutes.
Alerts sent to: your-email@example.com

---

## Support

For bugs or questions regarding this codebase:
Maiylsamy Durai — your-email@example.com
Response time: within 24 hours (business days)
