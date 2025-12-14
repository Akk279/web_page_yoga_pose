"""
API endpoints for authentication
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict
from .models import LoginRequest, RegisterRequest, AuthResponse, UserProfile
from .auth_manager import AuthManager
from .database import AuthDB

router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize auth manager and database
auth_manager = AuthManager()
auth_db = AuthDB()


def get_client_info(request: Request) -> tuple:
    """Extract client IP and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    return ip_address, user_agent


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, http_request: Request):
    """Register a new user"""
    try:
        response = auth_manager.register_user(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, http_request: Request):
    """Login user and create session"""
    try:
        ip_address, user_agent = get_client_info(http_request)
        response = auth_manager.login_user(request, ip_address, user_agent)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(session_id: str):
    """Logout user by removing session"""
    try:
        success = auth_manager.logout_user(session_id)
        if success:
            return {"success": True, "message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def validate_session(session_id: str):
    """Validate session and return user info"""
    try:
        is_valid, user = auth_manager.validate_session(session_id)
        if is_valid and user:
            return {
                "valid": True,
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email
            }
        else:
            return {"valid": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        profile = auth_db.get_user_profile(user_id)
        if profile:
            return profile.dict()
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile/{user_id}")
async def update_user_profile(user_id: str, profile_data: Dict):
    """Update user profile"""
    try:
        success, message = auth_manager.update_profile(user_id, profile_data)
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/change-password/{user_id}")
async def change_password(user_id: str, password_data: Dict):
    """Change user password"""
    try:
        old_password = password_data.get("old_password")
        new_password = password_data.get("new_password")
        
        if not old_password or not new_password:
            raise HTTPException(status_code=400, detail="Old and new passwords are required")
        
        success, message = auth_manager.change_password(user_id, old_password, new_password)
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics for dashboard"""
    try:
        stats = auth_manager.get_user_stats(user_id)
        if stats:
            return stats
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_all_users():
    """Get all users (admin only)"""
    try:
        users = auth_manager.get_all_users()
        return [{"user_id": user.user_id, "username": user.username, "is_active": user.is_active} for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup-sessions")
async def cleanup_sessions():
    """Clean up expired sessions"""
    try:
        auth_manager.cleanup_expired_sessions()
        return {"success": True, "message": "Expired sessions cleaned up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    try:
        user_count = auth_db.get_user_count()
        active_sessions = auth_db.get_active_sessions_count()
        
        return {
            "status": "healthy",
            "user_count": user_count,
            "active_sessions": active_sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
