# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from secure import Secure, ContentSecurityPolicy
from secure.middleware import SecureASGIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.core.errors import register_error_handlers
from app.db.database import get_db
from app.models import user
from app.routers import auth, users
# app/main.py — modify the FastAPI() initialization

app = FastAPI(
    title="Project One",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    # ↑ Ternary: if DEBUG=True (dev) → docs visible at /docs
    #            if DEBUG=False (production) → docs_url=None → /docs returns 404
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)
register_error_handlers(app)
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "disconnected"}
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins(),
    # ↑ Only these exact URLs can call your API from a browser
    # NEVER use ["*"] here in production — that's the vulnerability

    allow_credentials=True,
    # ↑ Allows cookies/auth headers to be sent cross-origin
    # Needed because your JWT goes in Authorization header

    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    # ↑ Which HTTP verbs are allowed — block anything not listed

    allow_headers=["Authorization", "Content-Type"],
    # ↑ Which request headers browser is allowed to send
    # Authorization = needed for your Bearer token
)

app.state.limiter = limiter
# ↑ Attaches limiter to app so it's accessible everywhere

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# ↑ When someone exceeds limit, this catches it and returns 
#   proper 429 "Too Many Requests" error automatically
if settings.DEBUG:
     # Dev mode — allow Swagger's CDN scripts/styles to load
    csp = (
        ContentSecurityPolicy()
        .default_src("'self'")
        .script_src("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
        .style_src("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
        .img_src("'self'", "data:", "https://fastapi.tiangolo.com")
    )
    secure_headers = Secure(csp=csp)
else:
    # Strict CSP for production — no Swagger exposed anyway (docs_url=None)
    secure_headers = Secure.with_default_headers()

app.add_middleware(SecureASGIMiddleware, secure=secure_headers) 