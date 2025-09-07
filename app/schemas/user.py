"""
User schemas for authentication and user management.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    """Model for user creation."""
    pass


class UserInDB(UserBase):
    """Model for user stored in database."""
    uid: str
    email_verified: bool = False
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """Model for user response."""
    pass


class Token(BaseModel):
    """Model for authentication token."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Model for token data."""
    uid: Optional[str] = None
    email: Optional[str] = None
