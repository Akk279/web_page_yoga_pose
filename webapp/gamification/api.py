"""
API endpoints for gamification features
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
from .models import UserProgress, PoseSession, Achievement, Leaderboard
from .database import GamificationDB
from .engine import GamificationEngine

router = APIRouter(prefix="/gamification", tags=["gamification"])

# Initialize database and engine
db = GamificationDB()
engine = GamificationEngine(db)


@router.get("/progress/{user_id}")
async def get_user_progress(user_id: str) -> Dict:
    """Get user's progress and statistics"""
    try:
        # Ensure progress exists for this user; auto-create on first access
        progress = db.get_user_progress(user_id)
        if progress is None:
            db.create_user_progress(user_id)
        stats = engine.get_user_stats(user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="User not found")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session")
async def submit_session(session_data: Dict) -> Dict:
    """Submit a completed pose session"""
    try:
        user_id = session_data.get("user_id")
        pose_name = session_data.get("pose_name")
        duration = session_data.get("duration", 0)
        accuracy = session_data.get("accuracy", 0.0)
        feedback = session_data.get("feedback", {})
        
        if not user_id or not pose_name:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        result = engine.process_session(user_id, pose_name, duration, accuracy, feedback)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements")
async def get_achievements() -> List[Achievement]:
    """Get all available achievements"""
    try:
        return db.get_achievements()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements/{user_id}")
async def get_user_achievements(user_id: str) -> List[Dict]:
    """Get user's earned achievements"""
    try:
        achievements = db.get_user_achievements(user_id)
        return [ach.dict() for ach in achievements]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10) -> List[Leaderboard]:
    """Get leaderboard"""
    try:
        return db.get_leaderboard(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-challenge")
async def get_daily_challenge() -> Optional[Dict]:
    """Get today's daily challenge"""
    try:
        challenge = db.get_today_challenge()
        if challenge:
            return challenge.dict()
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-challenge/complete")
async def complete_daily_challenge(completion_data: Dict) -> Dict:
    """Mark daily challenge as completed"""
    try:
        user_id = completion_data.get("user_id")
        challenge_id = completion_data.get("challenge_id")
        
        if not user_id or not challenge_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get challenge
        challenge = db.get_today_challenge()
        if not challenge or challenge.challenge_id != challenge_id:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Add user to completions if not already there
        if user_id not in challenge.completions:
            challenge.completions.append(user_id)
            db.create_daily_challenge(challenge)
            
            # Award XP
            progress = db.get_user_progress(user_id)
            if progress:
                progress.experience_points += challenge.reward_xp
                db.save_user_progress(progress)
        
        return {"completed": True, "reward_xp": challenge.reward_xp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str, limit: int = 50) -> List[Dict]:
    """Get user's recent sessions"""
    try:
        sessions = db.get_user_sessions(user_id, limit)
        return [session.dict() for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/create")
async def create_user(user_data: Dict) -> Dict:
    """Create a new user"""
    try:
        user_id = user_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Check if user already exists
        existing = db.get_user_progress(user_id)
        if existing:
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Create new user
        progress = db.create_user_progress(user_id)
        return {"user_id": user_id, "created": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/global")
async def get_global_stats() -> Dict:
    """Get global statistics"""
    try:
        # This would require aggregating data from all users
        # For now, return basic stats
        return {
            "total_users": 0,  # Would need to count users
            "total_sessions": 0,  # Would need to count all sessions
            "active_users_today": 0,  # Would need to count users who practiced today
            "most_popular_pose": "Unknown"  # Would need to analyze all sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
