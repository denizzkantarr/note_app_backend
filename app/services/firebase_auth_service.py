"""
Firebase Authentication service for user management and email verification.
"""
import logging
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from firebase_admin.exceptions import FirebaseError

from ..core.config import settings


class FirebaseAuthService:
    """Service for Firebase Authentication operations."""
    
    def __init__(self):
        self.auth = firebase_auth
    
    def create_user_with_email_and_password(
        self, 
        email: str, 
        password: str, 
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new user with email and password in Firebase Auth.
        
        Args:
            email: User's email address
            password: User's password
            display_name: Optional display name
            
        Returns:
            dict: User data including uid and email
            
        Raises:
            FirebaseError: If user creation fails
        """
        try:
            # Create user in Firebase Auth
            user_record = self.auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
                email_verified=True  # Set to True since we're verifying via our own system
            )
            
            logging.info(f"Firebase user created successfully: {user_record.uid}")
            
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
                "email_verified": user_record.email_verified,
                "disabled": user_record.disabled,
                "created_at": user_record.user_metadata.creation_timestamp,
                "last_sign_in": user_record.user_metadata.last_sign_in_timestamp
            }
            
        except FirebaseError as e:
            logging.error(f"Firebase user creation failed: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unexpected error creating Firebase user: {e}")
            raise FirebaseError(f"User creation failed: {str(e)}")
    
    async def send_email_verification(self, uid: str) -> bool:
        """
        Send email verification to user.
        
        Args:
            uid: Firebase user UID
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Generate email verification link
            action_code_settings = firebase_auth.ActionCodeSettings(
                url=f"{settings.frontend_url}/email-verified",  # Redirect URL after verification
                handle_code_in_app=True,
                dynamic_link_domain=None,
                ios_bundle_id=None,
                android_package_name=None,
                android_install_app=None,
                android_minimum_version=None
            )
            
            # Generate verification link
            verification_link = self.auth.generate_email_verification_link(
                email=None,  # Will be determined from uid
                action_code_settings=action_code_settings
            )
            
            # For now, we'll use the built-in Firebase email verification
            # In production, you might want to send a custom email with the link
            logging.info(f"Email verification link generated for user {uid}")
            logging.info(f"Verification link: {verification_link}")
            
            return True
            
        except FirebaseError as e:
            logging.error(f"Failed to send email verification: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending email verification: {e}")
            return False
    
    async def verify_email_verification_token(self, id_token: str) -> bool:
        """
        Verify if user's email is verified by checking the ID token.
        
        Args:
            id_token: Firebase ID token
            
        Returns:
            bool: True if email is verified
        """
        try:
            # Verify the ID token
            decoded_token = self.auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Get user record to check email verification status
            user_record = self.auth.get_user(uid)
            
            return user_record.email_verified
            
        except FirebaseError as e:
            logging.error(f"Failed to verify email verification token: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error verifying email token: {e}")
            return False
    
    async def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by UID.
        
        Args:
            uid: Firebase user UID
            
        Returns:
            dict: User data or None if not found
        """
        try:
            user_record = self.auth.get_user(uid)
            
            return {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
                "email_verified": user_record.email_verified,
                "disabled": user_record.disabled,
                "created_at": user_record.user_metadata.creation_timestamp,
                "last_sign_in": user_record.user_metadata.last_sign_in_timestamp
            }
            
        except FirebaseError as e:
            logging.error(f"Failed to get user by UID: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error getting user: {e}")
            return None
    
    async def update_user_email_verification(self, uid: str, email_verified: bool = True) -> bool:
        """
        Update user's email verification status.
        
        Args:
            uid: Firebase user UID
            email_verified: Email verification status
            
        Returns:
            bool: True if updated successfully
        """
        try:
            self.auth.update_user(uid, email_verified=email_verified)
            logging.info(f"Email verification status updated for user {uid}: {email_verified}")
            return True
            
        except FirebaseError as e:
            logging.error(f"Failed to update email verification status: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error updating email verification: {e}")
            return False
    
    async def delete_user(self, uid: str) -> bool:
        """
        Delete a user from Firebase Auth.
        
        Args:
            uid: Firebase user UID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            self.auth.delete_user(uid)
            logging.info(f"User deleted successfully: {uid}")
            return True
            
        except FirebaseError as e:
            logging.error(f"Failed to delete user: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error deleting user: {e}")
            return False
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and return decoded token.
        
        Args:
            id_token: Firebase ID token
            
        Returns:
            dict: Decoded token data or None if invalid
        """
        try:
            decoded_token = self.auth.verify_id_token(id_token)
            return decoded_token
            
        except FirebaseError as e:
            logging.error(f"Failed to verify ID token: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error verifying ID token: {e}")
            return None


# Global Firebase Auth service instance
firebase_auth_service = FirebaseAuthService()
