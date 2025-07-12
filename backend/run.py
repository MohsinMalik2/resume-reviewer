#!/usr/bin/env python3
"""
Auto Screener Agent Backend
Run script for development and production
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def main():
    """Main function to run the server"""
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3001))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🚀 Starting Auto Screener Agent Backend...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print("-" * 50)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug",
        access_log=True
    )

if __name__ == "__main__":
    main()