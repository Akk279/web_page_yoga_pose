"""
Authentication manager for handling login, logout, and session management
"""
from typing import Optional, Tuple
from datetime import datetime
import secrets
from .models import User, UserSession, LoginRequest, RegisterRequest, AuthResponse
from .database import AuthDB


class AuthManager:
    """Main authentication manager"""
    
    def __init__(self):
        self.db = AuthDB()
    
    def register_user(self, request: RegisterRequest) -> AuthResponse:
        """Register a new user"""
        try:
            # Validate input
            if not request.username or not request.password:
                return AuthResponse(
                    success=False,
                    message="Username and password are required"
                )
            
            if request.password != request.confirm_password:
                return AuthResponse(
                    success=False,
                    message="Passwords do not match"
                )
            
            if len(request.password) < 6:
                return AuthResponse(
                    success=False,
                    message="Password must be at least 6 characters long"
                )
            
            # Check if username already exists
            existing_user = self.db.get_user_by_username(request.username)
            if existing_user:
                return AuthResponse(
                    success=False,
                    message="Username already exists"
                )
            
            # Create new user
            user_id = self._generate_user_id()
            user = User(
                user_id=user_id,
                username=request.username,
                email=request.email,
                profile={"display_name": request.username}
            )
            user.set_password(request.password)
            
            # Save user
            if self.db.create_user(user):
                return AuthResponse(
                    success=True,
                    message="User registered successfully",
                    user_id=user_id,
                    username=user.username
                )
            else:
                return AuthResponse(
                    success=False,
                    message="Failed to create user"
                )
                
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Registration failed: {str(e)}"
            )
    
    def login_user(self, request: LoginRequest, ip_address: str = None, 
                   user_agent: str = None) -> AuthResponse:
        """Authenticate user and create session"""
        try:
            # Find user by username
            user = self.db.get_user_by_username(request.username)
            if not user:
                return AuthResponse(
                    success=False,
                    message="Invalid username or password"
                )
            
            # Check password
            if not user.check_password(request.password):
                return AuthResponse(
                    success=False,
                    message="Invalid username or password"
                )
            
            # Check if user is active
            if not user.is_active:
                return AuthResponse(
                    success=False,
                    message="Account is deactivated"
                )
            
            # Update last login
            user.last_login = datetime.now()
            self.db.update_user(user)
            
            # Create session
            session = UserSession.create_new(
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if self.db.create_session(session):
                return AuthResponse(
                    success=True,
                    message="Login successful",
                    session_id=session.session_id,
                    user_id=user.user_id,
                    username=user.username
                )
            else:
                return AuthResponse(
                    success=False,
                    message="Failed to create session"
                )
                
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Login failed: {str(e)}"
            )
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by removing session"""
        try:
            return self.db.remove_session(session_id)
        except Exception:
            return False
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[User]]:
        """Validate session and return user if valid"""
        try:
            session = self.db.get_session(session_id)
            if not session:
                return False, None
            
            user = self.db.get_user_by_id(session.user_id)
            if not user or not user.is_active:
                return False, None
            
            return True, user
        except Exception:
            return False, None
    
    def get_current_user(self, session_id: str) -> Optional[User]:
        """Get current user from session"""
        try:
            is_valid, user = self.validate_session(session_id)
            return user if is_valid else None
        except Exception:
            return None
    
    def change_password(self, user_id: str, old_password: str, 
                       new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        try:
            user = self.db.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            if not user.check_password(old_password):
                return False, "Current password is incorrect"
            
            if len(new_password) < 6:
                return False, "New password must be at least 6 characters long"
            
            user.set_password(new_password)
            if self.db.update_user(user):
                return True, "Password changed successfully"
            else:
                return False, "Failed to update password"
                
        except Exception as e:
            return False, f"Password change failed: {str(e)}"
    
    def update_profile(self, user_id: str, profile_data: dict) -> Tuple[bool, str]:
        """Update user profile"""
        try:
            if self.db.update_user_profile(user_id, profile_data):
                return True, "Profile updated successfully"
            else:
                return False, "Failed to update profile"
        except Exception as e:
            return False, f"Profile update failed: {str(e)}"
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get user statistics for dashboard"""
        try:
            user = self.db.get_user_by_id(user_id)
            if not user:
                return {}
            
            sessions = self.db.get_user_sessions(user_id)
            
            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at,
                "last_login": user.last_login,
                "active_sessions": len(sessions),
                "profile": user.profile
            }
        except Exception:
            return {}
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        self.db.cleanup_expired_sessions()
    
    @staticmethod
    def _generate_user_id() -> str:
        """Generate a unique user ID"""
        return f"user_{secrets.token_urlsafe(16)}"
    
    def get_all_users(self) -> list:
        """Get all users (for admin purposes)"""
        return self.db.get_all_users()
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        try:
            user = self.db.get_user_by_id(user_id)
            if user:
                user.is_active = False
                return self.db.update_user(user)
            return False
        except Exception:
            return False
    
    def activate_user(self, user_id: str) -> bool:
        """Activate a user account"""
        try:
            user = self.db.get_user_by_id(user_id)
            if user:
                user.is_active = True
                return self.db.update_user(user)
            return False
        except Exception:
            return False
