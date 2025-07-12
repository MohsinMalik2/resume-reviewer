from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

from app.models.user import UserCreate, UserLogin, UserResponse, AuthResponse, RefreshTokenRequest
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=AuthResponse)
async def register(user_create: UserCreate):
    """Register a new user"""
    try:
        # Create user
        user = AuthService.create_user(user_create)
        
        # Create tokens
        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Prepare user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            company=user.company,
            role=user.role,
            createdAt=user.createdAt
        )
        
        return AuthResponse(
            user=user_response,
            token=access_token,
            refreshToken=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login(user_login: UserLogin):
    """Login user"""
    try:
        # Authenticate user
        user = AuthService.authenticate_user(user_login.email, user_login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create tokens
        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Prepare user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            company=user.company,
            role=user.role,
            createdAt=user.createdAt
        )
        
        return AuthResponse(
            user=user_response,
            token=access_token,
            refreshToken=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    try:
        user = AuthService.get_current_user(credentials.credentials)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            company=user.company,
            role=user.role,
            createdAt=user.createdAt
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        access_token, new_refresh_token = AuthService.refresh_access_token(refresh_request.refreshToken)
        
        # Get user info for response
        token_data = AuthService.verify_token(new_refresh_token, "refresh")
        user = AuthService.get_current_user(access_token)
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            company=user.company,
            role=user.role,
            createdAt=user.createdAt
        )
        
        return AuthResponse(
            user=user_response,
            token=access_token,
            refreshToken=new_refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user (invalidate token)"""
    try:
        # Verify token is valid
        AuthService.get_current_user(credentials.credentials)
        
        # In a production system, you might want to blacklist the token
        # For now, we'll just return success
        
        return {"message": "Logged out successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )