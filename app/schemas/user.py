from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Min 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Need at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Need at least one number")
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True