"""
Authentication API endpoints with email verification and password security.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
import logging

from ..core.security import (
    PasswordSecurity, 
    EmailValidator, 
    get_current_user,
    require_email_verification
)
from ..core.database import firestore_service
from ..services.firebase_auth_service import firebase_auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserRegistration(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str
    confirm_password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str






@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """
    Register a new user directly in Firebase Authentication.
    
    Args:
        user_data: User registration data
        
    Returns:
        dict: Registration result
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Validate email format and domain
        is_valid_email, email_error = EmailValidator.validate_email(
            user_data.email,
            allowed_domains=None  # Allow all domains, can be configured
        )
        if not is_valid_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=email_error
            )
        
        # Validate password strength
        is_valid_password, password_error = PasswordSecurity.validate_password_strength(
            user_data.password
        )
        if not is_valid_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=password_error
            )
        
        # Check password confirmation
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if user already exists in Firebase Auth
        try:
            # Try to create user in Firebase Auth
            firebase_user = firebase_auth_service.create_user_with_email_and_password(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.name or user_data.email.split('@')[0]
            )
        except Exception as e:
            if "email-already-exists" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user account"
                )
        
        # Create user document in Firestore
        user_doc = {
            "email": user_data.email.lower(),
            "name": user_data.name or user_data.email.split('@')[0],
            "firebase_uid": firebase_user["uid"],
            "email_verified": True,  # Direct registration, no verification needed
            "created_at": __import__('datetime').datetime.utcnow(),
            "updated_at": __import__('datetime').datetime.utcnow(),
            "is_active": True
        }
        
        # Save user to Firestore using Firebase UID as document ID
        await firestore_service.create_document(
            collection_name="users",
            document_id=firebase_user["uid"],
            data=user_doc
        )
        
        logging.info(f"User created successfully: {user_data.email}")
        
        return {
            "message": "Registration successful. You can now log in.",
            "user_id": firebase_user["uid"],
            "email": user_data.email,
            "firebase_user": {
                "uid": firebase_user["uid"],
                "email": firebase_user["email"],
                "email_verified": firebase_user["email_verified"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"User registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )






@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(require_email_verification)):
    """
    Get current user profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: User profile information
        
    Raises:
        HTTPException: If profile retrieval fails
    """
    try:
        # Get user from database
        user_doc = await firestore_service.get_document_data(
            collection_name="users",
            document_id=current_user["uid"]
        )
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return profile without sensitive data
        profile = {
            "user_id": user_doc["id"],
            "email": user_doc["email"],
            "name": user_doc.get("name"),
            "email_verified": user_doc.get("email_verified", False),
            "created_at": user_doc.get("created_at"),
            "updated_at": user_doc.get("updated_at")
        }
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile. Please try again later."
        )
