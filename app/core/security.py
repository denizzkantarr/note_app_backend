"""
Security utilities for authentication and authorization.
"""
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
import hashlib
import secrets
import bcrypt

from .config import settings

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_credentials)
        firebase_admin.initialize_app(cred)
except Exception as e:
    logging.error(f"Failed to initialize Firebase Admin SDK: {e}")

# HTTP Bearer token scheme
security = HTTPBearer()


async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify Firebase ID token and return user information.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        dict: User information from Firebase token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Debug: Log the token being verified
        logging.info(f"Verifying Firebase token: {credentials.credentials[:20]}...")
        
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(credentials.credentials)
        
        # Debug: Log the decoded token
        logging.info(f"Token verified successfully for user: {decoded_token.get('uid')}")
        
        # Extract user information
        user_info = {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "email_verified": decoded_token.get("email_verified", False)
        }
        
        return user_info
        
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logging.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(user_info: dict = Depends(verify_firebase_token)) -> dict:
    """
    Get current authenticated user information.
    
    Args:
        user_info: User information from Firebase token
        
    Returns:
        dict: Current user information
    """
    return user_info


def require_email_verification(user_info: dict = Depends(get_current_user)) -> dict:
    """
    Require email verification for the current user.
    
    Args:
        user_info: Current user information
        
    Returns:
        dict: User information if email is verified
        
    Raises:
        HTTPException: If email is not verified
    """
    if not user_info.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please check your email and verify your account before accessing this feature."
        )
    return user_info


class PasswordSecurity:
    """Password security utilities with salted hashing."""
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt for password hashing."""
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:
        """
        Hash a password with salt using bcrypt.
        
        Args:
            password: Plain text password
            salt: Optional salt (if None, generates new salt)
            
        Returns:
            tuple: (hashed_password, salt)
        """
        if salt is None:
            salt = PasswordSecurity.generate_salt()
        
        # Combine password with salt
        salted_password = f"{password}{salt}".encode('utf-8')
        
        # Hash with bcrypt
        hashed = bcrypt.hashpw(salted_password, bcrypt.gensalt())
        
        return hashed.decode('utf-8'), salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored hashed password
            salt: Salt used for hashing
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            # Combine password with salt
            salted_password = f"{password}{salt}".encode('utf-8')
            
            # Verify with bcrypt
            return bcrypt.checkpw(salted_password, hashed_password.encode('utf-8'))
        except Exception as e:
            logging.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"


class EmailValidator:
    """Email validation utilities."""
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format using regex.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if email format is valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_allowed_domain(email: str, allowed_domains: list = None) -> bool:
        """
        Check if email domain is allowed.
        
        Args:
            email: Email address to check
            allowed_domains: List of allowed domains (if None, allows all)
            
        Returns:
            bool: True if domain is allowed
        """
        if allowed_domains is None:
            return True
        
        domain = email.split('@')[1].lower()
        return domain in [d.lower() for d in allowed_domains]
    
    @staticmethod
    def validate_email(email: str, allowed_domains: list = None) -> tuple[bool, str]:
        """
        Comprehensive email validation.
        
        Args:
            email: Email address to validate
            allowed_domains: List of allowed domains
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if not EmailValidator.validate_email_format(email):
            return False, "Invalid email format"
        
        if not EmailValidator.is_allowed_domain(email, allowed_domains):
            return False, f"Email domain not allowed. Allowed domains: {', '.join(allowed_domains)}"
        
        return True, "Email is valid"
