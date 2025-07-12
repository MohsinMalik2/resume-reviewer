from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routes import auth, resumes
from app.services.firebase_service import initialize_firebase
from app.services.ai_service import initialize_gemini

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Auto Screener Agent API...")
    
    # Initialize Firebase
    try:
        initialize_firebase()
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        raise
    
    # Initialize Gemini AI
    try:
        initialize_gemini()
        print("✅ Gemini AI initialized successfully")
    except Exception as e:
        print(f"❌ Gemini AI initialization failed: {e}")
        raise
    
    print("🎉 Auto Screener Agent API is ready!")
    yield
    
    # Shutdown
    print("👋 Shutting down Auto Screener Agent API...")

# Create FastAPI app
app = FastAPI(
    title="Auto Screener Agent API",
    description="AI-Powered Resume Screening & Rejection Automation for Recruiters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware (for production)
if not os.getenv("DEBUG", "True").lower() == "true":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly in production
    )

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Auto Screener Agent API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "auto-screener-agent",
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resume Processing"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Global exception: {exc}")
    return HTTPException(
        status_code=500,
        detail={
            "message": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3001))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )