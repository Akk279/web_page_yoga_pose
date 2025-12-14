"""
Authentication and user data models
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr
import hashlib
import secrets


class User(BaseModel):
    """User model for authentication and profile data"""
    user_id: str
    username: str
    email: Optional[str] = None
    password_hash: str = ""
    created_at: datetime = datetime.now()
    last_login: Optional[datetime] = None
    is_active: bool = True
    profile: Dict[str, Any] = {}
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = self._hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Check if password matches hash"""
        return self.password_hash == self._hash_password(password)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "yoga_app_salt_2024"  # In production, use random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()


class UserSession(BaseModel):
    """User session model for tracking active sessions"""
    session_id: str
    user_id: str
    created_at: datetime = datetime.now()
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @classmethod
    def create_new(cls, user_id: str, ip_address: str = None, user_agent: str = None) -> 'UserSession':
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now().replace(hour=23, minute=59, second=59)  # Expires at end of day
        
        return cls(
            session_id=session_id,
            user_id=user_id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request model"""
    username: str
    email: Optional[str] = None
    password: str
    confirm_password: str


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None


class UserProfile(BaseModel):
    """User profile model for dashboard"""
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Dict[str, Any] = {}
