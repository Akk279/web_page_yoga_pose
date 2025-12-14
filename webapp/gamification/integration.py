"""
Integration helpers for connecting gamification with the main app
"""
from typing import Dict, Optional
from datetime import datetime
from .database import GamificationDB
from .engine import GamificationEngine


class GamificationIntegration:
    """Helper class to integrate gamification with pose detection"""
    
    def __init__(self):
        self.db = GamificationDB()
        self.engine = GamificationEngine(self.db)
    
    def track_pose_session(self, user_id: str, pose_name: str, 
                          session_data: Dict) -> Dict:
        """
        Track a pose session from the main app
        
        Args:
            user_id: User identifier
            pose_name: Name of the pose being practiced
            session_data: Dictionary containing session information
                - duration: Session duration in seconds
                - accuracy: Average accuracy score (0.0 to 1.0)
                - feedback: Dictionary with feedback counts
                    - positive: Number of positive feedback instances
                    - negative: Number of negative feedback instances
                    - neutral: Number of neutral feedback instances
                    - total: Total number of feedback instances
        
        Returns:
            Dictionary with gamification results (XP gained, achievements, etc.)
        """
        duration = session_data.get('duration', 0)
        accuracy = session_data.get('accuracy', 0.0)
        feedback = session_data.get('feedback', {})
        
        # Process the session through gamification engine
        result = self.engine.process_session(
            user_id=user_id,
            pose_name=pose_name,
            duration=duration,
            accuracy=accuracy,
            feedback=feedback
        )
        
        return result
    
    def get_user_progress_summary(self, user_id: str) -> Optional[Dict]:
        """Get a summary of user progress for display in the main app"""
        try:
            stats = self.engine.get_user_stats(user_id)
            if not stats:
                return None
            
            # Return a simplified summary
            return {
                'level': stats['progress']['level'],
                'level_name': stats['level_info'].get('name', 'Beginner'),
                'total_xp': stats['progress']['experience_points'],
                'current_streak': stats['progress']['current_streak'],
                'total_sessions': stats['progress']['total_sessions'],
                'poses_learned': len(stats['progress']['poses_learned']),
                'achievements_count': len(stats['achievements']),
                'next_level_xp': stats.get('next_level_xp')
            }
        except Exception:
            return None
    
    def should_show_achievement_notification(self, user_id: str) -> Optional[Dict]:
        """Check if we should show an achievement notification"""
        # This would typically check for recently earned achievements
        # For now, return None (no notification)
        return None
    
    def get_daily_challenge_info(self) -> Optional[Dict]:
        """Get today's daily challenge information"""
        try:
            challenge = self.db.get_today_challenge()
            if challenge:
                return {
                    'id': challenge.challenge_id,
                    'name': challenge.name,
                    'description': challenge.description,
                    'target_pose': challenge.target_pose,
                    'target_duration': challenge.target_duration,
                    'reward_xp': challenge.reward_xp
                }
        except Exception:
            pass
        return None
    
    def complete_daily_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Mark daily challenge as completed for user"""
        try:
            challenge = self.db.get_today_challenge()
            if challenge and challenge.challenge_id == challenge_id:
                if user_id not in challenge.completions:
                    challenge.completions.append(user_id)
                    self.db.create_daily_challenge(challenge)
                    
                    # Award XP
                    progress = self.db.get_user_progress(user_id)
                    if progress:
                        progress.experience_points += challenge.reward_xp
                        self.db.save_user_progress(progress)
                    return True
        except Exception:
            pass
        return False


# Global instance for easy access
gamification = GamificationIntegration()


def track_pose_detection(user_id: str, pose_name: str, confidence: float, 
                        feedback_type: str = 'neutral') -> Dict:
    """
    Convenience function to track pose detection results
    
    Args:
        user_id: User identifier
        pose_name: Detected pose name
        confidence: Detection confidence (0.0 to 1.0)
        feedback_type: Type of feedback ('positive', 'negative', 'neutral')
    
    Returns:
        Gamification results dictionary
    """
    # This would typically be called from the pose detection system
    # For now, return empty result
    return {
        'xp_gained': 0,
        'new_level': None,
        'new_achievements': [],
        'current_streak': 0,
        'total_xp': 0
    }


def get_user_dashboard_data(user_id: str) -> Dict:
    """
    Get all data needed for the user dashboard
    
    Args:
        user_id: User identifier
    
    Returns:
        Dictionary with all dashboard data
    """
    try:
        # Get user progress
        progress_summary = gamification.get_user_progress_summary(user_id)
        if not progress_summary:
            return {'error': 'User not found'}
        
        # Get daily challenge
        daily_challenge = gamification.get_daily_challenge_info()
        
        # Get leaderboard position (simplified)
        leaderboard = gamification.db.get_leaderboard(limit=100)
        user_rank = None
        for i, entry in enumerate(leaderboard):
            if entry.user_id == user_id:
                user_rank = i + 1
                break
        
        return {
            'progress': progress_summary,
            'daily_challenge': daily_challenge,
            'leaderboard_rank': user_rank,
            'total_users': len(leaderboard)
        }
    except Exception as e:
        return {'error': str(e)}
