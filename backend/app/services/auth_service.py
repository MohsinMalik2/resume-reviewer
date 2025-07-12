from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os

from app.models.user import UserCreate, UserInDB, TokenData
from app.services.firebase_service import FirebaseService

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "30"))

class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise credentials_exception
            
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None or user_id is None:
                raise credentials_exception
                
            token_data = TokenData(email=email, user_id=user_id)
            return token_data
            
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user_data = FirebaseService.get_user_by_email(email)
        
        if not user_data:
            return None
        
        user = UserInDB(**user_data)
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def create_user(user_create: UserCreate) -> UserInDB:
        """Create a new user"""
        # Check if user already exists
        existing_user = FirebaseService.get_user_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = AuthService.get_password_hash(user_create.password)
        
        # Prepare user data
        now = datetime.utcnow()
        user_data = {
            "email": user_create.email,
            "firstName": user_create.firstName,
            "lastName": user_create.lastName,
            "company": user_create.company,
            "role": user_create.role,
            "hashed_password": hashed_password,
            "createdAt": now,
            "updatedAt": now
        }
        
        # Create user in Firebase
        user_id = FirebaseService.create_user(user_data)
        user_data["id"] = user_id
        
        return UserInDB(**user_data)
    
    @staticmethod
    def get_current_user(token: str) -> UserInDB:
        """Get current user from token"""
        token_data = AuthService.verify_token(token)
        
        user_data = FirebaseService.get_user_by_id(token_data.user_id)
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return UserInDB(**user_data)
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> tuple[str, str]:
        """Refresh access token using refresh token"""
        token_data = AuthService.verify_token(refresh_token, "refresh")
        
        # Verify user still exists
        user_data = FirebaseService.get_user_by_id(token_data.user_id)
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        access_token = AuthService.create_access_token(
            data={"sub": token_data.email, "user_id": token_data.user_id}
        )
        new_refresh_token = AuthService.create_refresh_token(
            data={"sub": token_data.email, "user_id": token_data.user_id}
        )
        
        return access_token, new_refresh_token