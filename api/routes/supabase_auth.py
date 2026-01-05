from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from supabase import create_client
from api.core.config import settings
from api.core.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Lazy initialization of Supabase clients
_supabase = None
_supabase_admin = None


def get_supabase():
    """Get or create Supabase client (use anon key for public endpoints)"""
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _supabase


def get_supabase_admin():
    """Get or create Supabase admin client (use service role key)"""
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _supabase_admin


# Request/Response Models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user: dict


# Auth Endpoints
@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Sign up a new user with email and password.
    User will be created in Supabase Auth.
    """
    try:
        # Create user with metadata
        response = get_supabase().auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": request.full_name or request.email.split("@")[0],
                    }
                },
            }
        )

        if response.user:
            return {
                "access_token": response.session.access_token if response.session else "",
                "refresh_token": response.session.refresh_token if response.session else None,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": str(response.user.created_at),
                },
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    Returns access token and refresh token.
    """
    try:
        response = get_supabase().auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                },
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh an expired access token using a refresh token.
    """
    try:
        response = get_supabase().auth.refresh_session(refresh_token)
        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token",
        )


@router.get("/debug/decode-token")
async def debug_decode_token(token: str):
    """
    DEBUG ONLY: Decode and inspect a token without verification.
    Shows the header and payload for debugging.
    Remove this in production.
    """
    try:
        from jwt import get_unverified_header, decode as jwt_decode
        import json
        
        header = get_unverified_header(token)
        payload = jwt_decode(token, options={"verify_signature": False})
        
        return {
            "header": header,
            "payload": payload,
            "algorithm": header.get("alg"),
            "key_id": header.get("kid"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decode token: {str(e)}",
        )


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info from token.
    Protected endpoint - requires valid JWT.
    """
    return {
        "user": user,
        "message": f"Hello {user.get('email')}!",
    }


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """
    Logout current user (revoke token on client side).
    This endpoint just validates the token is still valid.
    """
    return {
        "message": f"User {user.get('email')} logged out successfully",
        "user_id": user.get("id"),
    }


@router.post("/set-user-role")
async def set_user_role(
    user_id: str,
    role: str,
    admin: dict = Depends(get_current_admin),
):
    """
    Admin only: Set user role (e.g., admin, moderator, user).
    """
    try:
        get_supabase_admin().auth.admin_update_user_by_id(
            user_id,
            {"app_metadata": {"role": role}},
        )
        return {
            "message": f"User role updated to {role}",
            "user_id": user_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user role: {str(e)}",
        )


@router.get("/users")
async def list_users(admin: dict = Depends(get_current_admin)):
    """
    Admin only: List all users.
    """
    try:
        response = get_supabase_admin().auth.admin_list_users()
        return {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "created_at": str(user.created_at),
                }
                for user in response.users
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list users: {str(e)}",
        )
