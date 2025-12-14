"""
Database operations for gamification features
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from .models import (
    UserProgress, PoseSession, Achievement, UserAchievement, 
    Level, DailyChallenge, Leaderboard
)


class GamificationDB:
    """Simple file-based database for gamification data"""
    
    def __init__(self, data_dir: str = "data/gamification"):
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
    
    # User Progress Operations
    def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Get user progress data"""
        data = self._load_json("user_progress.json")
        if user_id in data:
            return UserProgress(**data[user_id])
        return None
    
    def save_user_progress(self, progress: UserProgress):
        """Save user progress data"""
        data = self._load_json("user_progress.json")
        progress.updated_at = datetime.now()
        data[progress.user_id] = progress.dict()
        self._save_json("user_progress.json", data)
    
    def create_user_progress(self, user_id: str) -> UserProgress:
        """Create new user progress"""
        progress = UserProgress(user_id=user_id)
        self.save_user_progress(progress)
        return progress
    
    # Pose Session Operations
    def save_pose_session(self, session: PoseSession):
        """Save pose session data"""
        data = self._load_json("pose_sessions.json")
        if "sessions" not in data:
            data["sessions"] = []
        data["sessions"].append(session.dict())
        self._save_json("pose_sessions.json", data)
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[PoseSession]:
        """Get user's recent sessions"""
        data = self._load_json("pose_sessions.json")
        sessions = []
        if "sessions" in data:
            for session_data in data["sessions"][-limit:]:
                if session_data.get("user_id") == user_id:
                    sessions.append(PoseSession(**session_data))
        return sessions
    
    # Achievement Operations
    def get_achievements(self) -> List[Achievement]:
        """Get all available achievements"""
        data = self._load_json("achievements.json")
        if "achievements" not in data:
            # Initialize default achievements
            self._initialize_default_achievements()
            data = self._load_json("achievements.json")
        
        return [Achievement(**ach) for ach in data["achievements"]]
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get user's earned achievements"""
        data = self._load_json("user_achievements.json")
        achievements = []
        if user_id in data:
            for ach_data in data[user_id]:
                achievements.append(UserAchievement(**ach_data))
        return achievements
    
    def award_achievement(self, user_id: str, achievement_id: str):
        """Award achievement to user"""
        data = self._load_json("user_achievements.json")
        if user_id not in data:
            data[user_id] = []
        
        # Check if already awarded
        for ach in data[user_id]:
            if ach["achievement_id"] == achievement_id:
                return  # Already awarded
        
        # Award achievement
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            earned_at=datetime.now()
        )
        data[user_id].append(user_achievement.dict())
        self._save_json("user_achievements.json", data)
    
    # Daily Challenge Operations
    def get_today_challenge(self) -> Optional[DailyChallenge]:
        """Get today's daily challenge"""
        data = self._load_json("daily_challenges.json")
        today = date.today().isoformat()
        if today in data:
            return DailyChallenge(**data[today])
        return None
    
    def create_daily_challenge(self, challenge: DailyChallenge):
        """Create daily challenge"""
        data = self._load_json("daily_challenges.json")
        data[challenge.date.isoformat()] = challenge.dict()
        self._save_json("daily_challenges.json", data)
    
    # Leaderboard Operations
    def get_leaderboard(self, limit: int = 10) -> List[Leaderboard]:
        """Get leaderboard"""
        data = self._load_json("user_progress.json")
        leaderboard = []
        
        for user_id, progress_data in data.items():
            progress = UserProgress(**progress_data)
            leaderboard.append(Leaderboard(
                user_id=user_id,
                username=user_id,  # Default to user_id, can be enhanced
                total_xp=progress.experience_points,
                level=progress.level,
                current_streak=progress.current_streak,
                rank=0  # Will be calculated
            ))
        
        # Sort by XP and assign ranks
        leaderboard.sort(key=lambda x: x.total_xp, reverse=True)
        for i, entry in enumerate(leaderboard[:limit]):
            entry.rank = i + 1
        
        return leaderboard[:limit]
    
    def _initialize_default_achievements(self):
        """Initialize default achievements"""
        achievements = [
            {
                "achievement_id": "first_session",
                "name": "First Steps",
                "description": "Complete your first yoga session",
                "icon": "🌱",
                "requirements": {"sessions": 1},
                "reward_xp": 50,
                "category": "practice"
            },
            {
                "achievement_id": "week_streak",
                "name": "Consistent Practice",
                "description": "Practice for 7 days in a row",
                "icon": "🔥",
                "requirements": {"streak": 7},
                "reward_xp": 200,
                "category": "streak"
            },
            {
                "achievement_id": "pose_master",
                "name": "Pose Master",
                "description": "Master 10 different poses",
                "icon": "🧘‍♀️",
                "requirements": {"poses_learned": 10},
                "reward_xp": 300,
                "category": "pose"
            },
            {
                "achievement_id": "hour_practice",
                "name": "Hour of Power",
                "description": "Practice for a total of 60 minutes",
                "icon": "⏰",
                "requirements": {"total_time": 60},
                "reward_xp": 150,
                "category": "time"
            }
        ]
        
        data = {"achievements": achievements}
        self._save_json("achievements.json", data)
