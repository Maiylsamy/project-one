from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, LoginRequest
from app.services.user_service import create_user, authenticate_user
from app.core.security import create_access_token
# ↑ added "Request" import — required by slowapi to read IP address
from app.core.limiter import limiter  # ← new import

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/hour") 
# ↑ decorator MUST be directly above the function
# Max 3 registration attempts per hour per IP — stops mass fake accounts
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    # ↑ "request: Request" parameter is REQUIRED here
    # slowapi reads the caller's IP from this — without it, decorator crashes
    user = create_user(db, user_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user

@router.post("/login", response_model=Token)
@limiter.limit("5/hour")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}