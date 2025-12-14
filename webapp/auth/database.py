"""
Database operations for authentication and user management
"""
import json
import os
from typing import Optional, Dict, List
from datetime import datetime
from .models import User, UserSession, UserProfile


class AuthDB:
    """Simple file-based database for authentication data"""
    
    def __init__(self, data_dir: str = "data/auth"):
        self.data_dir = data_dir
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_file_path(self, filename: str) -> str:
        """Get full path for data file"""
        return os.path.join(self.data_dir, filename)
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON data from file"""
        file_path = self._get_file_path(filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_json(self, filename: str, data: Dict):
        """Save JSON data to file"""
        file_path = self._get_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    # User Operations
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            data = self._load_json("users.json")
            
            # Check if username already exists
            for existing_user in data.values():
                if existing_user.get("username") == user.username:
                    return False
            
            data[user.user_id] = user.dict()
            self._save_json("users.json", data)
            return True
        except Exception:
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user ID"""
        try:
            data = self._load_json("users.json")
            if user_id in data:
                return User(**data[user_id])
            return None
        except Exception:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            data = self._load_json("users.json")
            for user_data in data.values():
                if user_data.get("username") == username:
                    return User(**user_data)
            return None
        except Exception:
            return None
    
    def update_user(self, user: User) -> bool:
        """Update user data"""
        try:
            data = self._load_json("users.json")
            if user.user_id in data:
                data[user.user_id] = user.dict()
                self._save_json("users.json", data)
                return True
            return False
        except Exception:
            return False
    
    def get_all_users(self) -> List[User]:
        """Get all users (for admin purposes)"""
        try:
            data = self._load_json("users.json")
            return [User(**user_data) for user_data in data.values()]
        except Exception:
            return []
    
    # Session Operations
    def create_session(self, session: UserSession) -> bool:
        """Create a new user session"""
        try:
            data = self._load_json("sessions.json")
            if "sessions" not in data:
                data["sessions"] = []
            
            data["sessions"].append(session.dict())
            self._save_json("sessions.json", data)
            return True
        except Exception:
            return False
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by session ID"""
        try:
            data = self._load_json("sessions.json")
            if "sessions" in data:
                for session_data in data["sessions"]:
                    if session_data.get("session_id") == session_id:
                        session = UserSession(**session_data)
                        if not session.is_expired():
                            return session
                        else:
                            # Remove expired session
                            self.remove_session(session_id)
            return None
        except Exception:
            return None
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        try:
            data = self._load_json("sessions.json")
            if "sessions" in data:
                data["sessions"] = [
                    s for s in data["sessions"] 
                    if s.get("session_id") != session_id
                ]
                self._save_json("sessions.json", data)
            return True
        except Exception:
            return False
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        try:
            data = self._load_json("sessions.json")
            if "sessions" in data:
                current_time = datetime.now()
                data["sessions"] = [
                    s for s in data["sessions"]
                    if datetime.fromisoformat(s.get("expires_at", "1970-01-01")) > current_time
                ]
                self._save_json("sessions.json", data)
        except Exception:
            pass
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active sessions for a user"""
        try:
            data = self._load_json("sessions.json")
            sessions = []
            if "sessions" in data:
                for session_data in data["sessions"]:
                    if session_data.get("user_id") == user_id:
                        session = UserSession(**session_data)
                        if not session.is_expired():
                            sessions.append(session)
            return sessions
        except Exception:
            return []
    
    # Profile Operations
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile for dashboard"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                return UserProfile(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    created_at=user.created_at,
                    last_login=user.last_login,
                    profile=user.profile
                )
            return None
        except Exception:
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user profile data"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.profile.update(profile_data)
                return self.update_user(user)
            return False
        except Exception:
            return False
    
    # Statistics
    def get_user_count(self) -> int:
        """Get total number of users"""
        try:
            data = self._load_json("users.json")
            return len(data)
        except Exception:
            return 0
    
    def get_active_sessions_count(self) -> int:
        """Get number of active sessions"""
        try:
            self.cleanup_expired_sessions()
            data = self._load_json("sessions.json")
            return len(data.get("sessions", []))
        except Exception:
            return 0
