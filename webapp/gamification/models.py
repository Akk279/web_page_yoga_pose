"""
Gamification data models for user progress tracking
"""
from typing import Dict, List, Optional
from datetime import datetime, date
from pydantic import BaseModel


class UserProgress(BaseModel):
    """User progress tracking model"""
    user_id: str
    total_sessions: int = 0
    total_practice_time: int = 0  # in minutes
    poses_learned: List[str] = []
    current_streak: int = 0
    longest_streak: int = 0
    last_practice_date: Optional[date] = None
    level: int = 1
    experience_points: int = 0
    achievements: List[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class PoseSession(BaseModel):
    """Individual pose practice session"""
    session_id: str
    user_id: str
    pose_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int = 0  # in seconds
    accuracy_score: float = 0.0  # 0.0 to 1.0
    attempts: int = 0
    successful_attempts: int = 0
    feedback_count: Dict[str, int] = {}  # positive, negative, neutral


class Achievement(BaseModel):
    """Achievement definition"""
    achievement_id: str
    name: str
    description: str
    icon: str
    requirements: Dict[str, int]  # criteria for unlocking
    reward_xp: int
    category: str  # "practice", "streak", "pose", "time"


class UserAchievement(BaseModel):
    """User's earned achievements"""
    user_id: str
    achievement_id: str
    earned_at: datetime
    progress: Dict[str, int] = {}  # current progress toward achievement


class Level(BaseModel):
    """User level definition"""
    level: int
    name: str
    required_xp: int
    rewards: List[str] = []
    description: str = ""


class DailyChallenge(BaseModel):
    """Daily challenge for users"""
    challenge_id: str
    date: date
    name: str
    description: str
    target_pose: str
    target_duration: int  # in minutes
    reward_xp: int
    participants: List[str] = []  # user_ids
    completions: List[str] = []  # user_ids who completed


class Leaderboard(BaseModel):
    """Leaderboard entry"""
    user_id: str
    username: str
    total_xp: int
    level: int
    current_streak: int
    rank: int
    avatar: Optional[str] = None
