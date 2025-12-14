"""
Gamification engine for calculating progress, achievements, and rewards
"""
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from .models import UserProgress, PoseSession, Achievement, UserAchievement
from .database import GamificationDB


class GamificationEngine:
    """Main gamification logic engine"""
    
    def __init__(self, db: GamificationDB):
        self.db = db
        self.levels = self._initialize_levels()
    
    def _initialize_levels(self) -> Dict[int, Dict]:
        """Initialize level system"""
        return {
            1: {"name": "Beginner", "required_xp": 0, "description": "Starting your yoga journey"},
            2: {"name": "Novice", "required_xp": 100, "description": "Getting the hang of it"},
            3: {"name": "Apprentice", "required_xp": 300, "description": "Building your practice"},
            4: {"name": "Practitioner", "required_xp": 600, "description": "Regular practice"},
            5: {"name": "Dedicated", "required_xp": 1000, "description": "Committed to yoga"},
            6: {"name": "Advanced", "required_xp": 1500, "description": "Advanced practitioner"},
            7: {"name": "Expert", "required_xp": 2200, "description": "Yoga expert"},
            8: {"name": "Master", "required_xp": 3000, "description": "Yoga master"},
            9: {"name": "Guru", "required_xp": 4000, "description": "Yoga guru"},
            10: {"name": "Enlightened", "required_xp": 5000, "description": "Enlightened being"}
        }
    
    def process_session(self, user_id: str, pose_name: str, duration: int, 
                       accuracy: float, feedback: Dict[str, int]) -> Dict:
        """Process a completed pose session and update progress"""
        # Get or create user progress
        progress = self.db.get_user_progress(user_id)
        if not progress:
            progress = self.db.create_user_progress(user_id)
        
        # Create session record
        session = PoseSession(
            session_id=f"{user_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            pose_name=pose_name,
            start_time=datetime.now() - timedelta(seconds=duration),
            end_time=datetime.now(),
            duration=duration,
            accuracy_score=accuracy,
            attempts=feedback.get("total", 1),
            successful_attempts=feedback.get("positive", 0),
            feedback_count=feedback
        )
        
        # Save session
        self.db.save_pose_session(session)
        
        # Update progress
        old_level = progress.level
        progress = self._update_progress(progress, session)
        
        # Check for achievements
        new_achievements = self._check_achievements(progress)
        
        # Calculate XP gained
        xp_gained = self._calculate_xp(session, progress)
        progress.experience_points += xp_gained
        
        # Check level up
        new_level = self._calculate_level(progress.experience_points)
        level_up = new_level > old_level
        if level_up:
            progress.level = new_level
        
        # Update streak
        self._update_streak(progress)
        
        # Save updated progress
        self.db.save_user_progress(progress)
        
        return {
            "xp_gained": xp_gained,
            "new_level": new_level if level_up else None,
            "new_achievements": new_achievements,
            "current_streak": progress.current_streak,
            "total_xp": progress.experience_points
        }
    
    def _update_progress(self, progress: UserProgress, session: PoseSession) -> UserProgress:
        """Update user progress based on session"""
        progress.total_sessions += 1
        progress.total_practice_time += session.duration // 60  # Convert to minutes
        
        # Add pose to learned poses if not already there
        if session.pose_name not in progress.poses_learned:
            progress.poses_learned.append(session.pose_name)
        
        progress.last_practice_date = date.today()
        return progress
    
    def _calculate_xp(self, session: PoseSession, progress: UserProgress) -> int:
        """Calculate XP gained from session"""
        base_xp = 10
        
        # Duration bonus (1 XP per minute)
        duration_bonus = session.duration // 60
        
        # Accuracy bonus
        accuracy_bonus = int(session.accuracy_score * 20)
        
        # Streak bonus
        streak_bonus = min(progress.current_streak * 2, 20)
        
        # New pose bonus
        new_pose_bonus = 25 if session.pose_name not in progress.poses_learned else 0
        
        total_xp = base_xp + duration_bonus + accuracy_bonus + streak_bonus + new_pose_bonus
        return total_xp
    
    def _calculate_level(self, total_xp: int) -> int:
        """Calculate user level based on total XP"""
        for level, data in reversed(self.levels.items()):
            if total_xp >= data["required_xp"]:
                return level
        return 1
    
    def _update_streak(self, progress: UserProgress):
        """Update user's practice streak"""
        today = date.today()
        
        if progress.last_practice_date:
            days_diff = (today - progress.last_practice_date).days
            
            if days_diff == 0:
                # Same day, no change
                return
            elif days_diff == 1:
                # Consecutive day
                progress.current_streak += 1
            else:
                # Streak broken
                progress.current_streak = 1
        else:
            # First practice
            progress.current_streak = 1
        
        # Update longest streak
        if progress.current_streak > progress.longest_streak:
            progress.longest_streak = progress.current_streak
    
    def _check_achievements(self, progress: UserProgress) -> List[str]:
        """Check and award new achievements"""
        achievements = self.db.get_achievements()
        user_achievements = self.db.get_user_achievements(progress.user_id)
        earned_achievement_ids = {ach.achievement_id for ach in user_achievements}
        
        new_achievements = []
        
        for achievement in achievements:
            if achievement.achievement_id in earned_achievement_ids:
                continue  # Already earned
            
            # Check if requirements are met
            if self._check_achievement_requirements(achievement, progress):
                self.db.award_achievement(progress.user_id, achievement.achievement_id)
                new_achievements.append(achievement.achievement_id)
        
        return new_achievements
    
    def _check_achievement_requirements(self, achievement: Achievement, 
                                      progress: UserProgress) -> bool:
        """Check if user meets achievement requirements"""
        for requirement, target_value in achievement.requirements.items():
            if requirement == "sessions":
                if progress.total_sessions < target_value:
                    return False
            elif requirement == "streak":
                if progress.current_streak < target_value:
                    return False
            elif requirement == "poses_learned":
                if len(progress.poses_learned) < target_value:
                    return False
            elif requirement == "total_time":
                if progress.total_practice_time < target_value:
                    return False
        
        return True
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get comprehensive user statistics"""
        progress = self.db.get_user_progress(user_id)
        if not progress:
            return {}
        
        sessions = self.db.get_user_sessions(user_id, limit=100)
        achievements = self.db.get_achievements()
        user_achievements = self.db.get_user_achievements(user_id)
        
        # Calculate additional stats
        total_accuracy = sum(s.accuracy_score for s in sessions) / len(sessions) if sessions else 0
        favorite_pose = self._get_favorite_pose(sessions)
        weekly_stats = self._get_weekly_stats(sessions)
        
        return {
            "progress": progress.dict(),
            "total_sessions": len(sessions),
            "average_accuracy": round(total_accuracy, 2),
            "favorite_pose": favorite_pose,
            "weekly_stats": weekly_stats,
            "achievements": [ach.dict() for ach in user_achievements],
            "available_achievements": len(achievements),
            "level_info": self.levels.get(progress.level, {}),
            "next_level_xp": self._get_next_level_xp(progress.experience_points)
        }
    
    def _get_favorite_pose(self, sessions: List[PoseSession]) -> Optional[str]:
        """Get user's most practiced pose"""
        if not sessions:
            return None
        
        pose_counts = {}
        for session in sessions:
            pose_counts[session.pose_name] = pose_counts.get(session.pose_name, 0) + 1
        
        return max(pose_counts.items(), key=lambda x: x[1])[0]
    
    def _get_weekly_stats(self, sessions: List[PoseSession]) -> Dict:
        """Get weekly practice statistics"""
        now = datetime.now()
        week_start = now - timedelta(days=7)
        
        weekly_sessions = [s for s in sessions if s.start_time >= week_start]
        
        return {
            "sessions_this_week": len(weekly_sessions),
            "time_this_week": sum(s.duration for s in weekly_sessions) // 60,
            "poses_this_week": len(set(s.pose_name for s in weekly_sessions))
        }
    
    def _get_next_level_xp(self, current_xp: int) -> Optional[int]:
        """Get XP required for next level"""
        current_level = self._calculate_level(current_xp)
        next_level = current_level + 1
        
        if next_level in self.levels:
            return self.levels[next_level]["required_xp"] - current_xp
        return None
