# Gamification Module

This module adds gamification features to the yoga app, including progress tracking, achievements, levels, and leaderboards.

## Features

### 🎯 Progress Tracking
- **User Levels**: 10 levels from Beginner to Enlightened
- **Experience Points (XP)**: Earned through practice sessions
- **Practice Streaks**: Track consecutive days of practice
- **Session Statistics**: Duration, accuracy, poses learned

### 🏆 Achievements System
- **Practice Achievements**: First session, consistent practice
- **Pose Achievements**: Master different poses
- **Time Achievements**: Practice for extended periods
- **Streak Achievements**: Maintain practice streaks

### 📊 Dashboard
- **Progress Overview**: Level, XP, streaks, sessions
- **Achievement Gallery**: Visual display of earned achievements
- **Weekly Statistics**: Practice summary for current week
- **Leaderboard**: Compare with other users

### 🎮 Daily Challenges
- **Daily Goals**: Specific poses or practice targets
- **Reward System**: XP bonuses for completing challenges
- **Community Participation**: See who else is participating

## File Structure

```
webapp/gamification/
├── __init__.py          # Module initialization
├── models.py            # Data models (Pydantic)
├── database.py          # File-based database operations
├── engine.py            # Core gamification logic
├── api.py               # FastAPI endpoints
├── integration.py       # Integration helpers
└── README.md           # This file
```

## API Endpoints

### User Progress
- `GET /gamification/progress/{user_id}` - Get user progress and stats
- `POST /gamification/session` - Submit completed session
- `GET /gamification/sessions/{user_id}` - Get user's recent sessions

### Achievements
- `GET /gamification/achievements` - Get all available achievements
- `GET /gamification/achievements/{user_id}` - Get user's earned achievements

### Leaderboard
- `GET /gamification/leaderboard` - Get leaderboard

### Daily Challenges
- `GET /gamification/daily-challenge` - Get today's challenge
- `POST /gamification/daily-challenge/complete` - Complete challenge

## Usage

### Basic Integration

```python
from webapp.gamification.integration import gamification

# Track a pose session
result = gamification.track_pose_session(
    user_id="user123",
    pose_name="Downward Dog",
    session_data={
        'duration': 300,  # 5 minutes
        'accuracy': 0.85,
        'feedback': {
            'positive': 3,
            'negative': 1,
            'neutral': 2,
            'total': 6
        }
    }
)

# Get user progress summary
progress = gamification.get_user_progress_summary("user123")
```

### XP Calculation

XP is awarded based on:
- **Base XP**: 10 points per session
- **Duration Bonus**: 1 XP per minute of practice
- **Accuracy Bonus**: Up to 20 XP based on pose accuracy
- **Streak Bonus**: Up to 20 XP for consecutive days
- **New Pose Bonus**: 25 XP for trying a new pose

### Level System

| Level | Name | Required XP | Description |
|-------|------|-------------|-------------|
| 1 | Beginner | 0 | Starting your yoga journey |
| 2 | Novice | 100 | Getting the hang of it |
| 3 | Apprentice | 300 | Building your practice |
| 4 | Practitioner | 600 | Regular practice |
| 5 | Dedicated | 1000 | Committed to yoga |
| 6 | Advanced | 1500 | Advanced practitioner |
| 7 | Expert | 2200 | Yoga expert |
| 8 | Master | 3000 | Yoga master |
| 9 | Guru | 4000 | Yoga guru |
| 10 | Enlightened | 5000 | Enlightened being |

## Data Storage

The module uses a simple file-based storage system:
- `data/gamification/user_progress.json` - User progress data
- `data/gamification/pose_sessions.json` - Session history
- `data/gamification/achievements.json` - Achievement definitions
- `data/gamification/user_achievements.json` - User achievement records
- `data/gamification/daily_challenges.json` - Daily challenge data

## Dashboard

Access the progress dashboard at `/dashboard` to see:
- Current level and XP progress
- Practice statistics
- Earned achievements
- Weekly summary
- Leaderboard position

## Future Enhancements

- **Social Features**: Friend system, sharing achievements
- **Custom Challenges**: User-created challenges
- **Rewards System**: Unlockable content, badges
- **Analytics**: Detailed practice analytics
- **Mobile App**: Native mobile dashboard
- **Notifications**: Achievement and streak reminders
