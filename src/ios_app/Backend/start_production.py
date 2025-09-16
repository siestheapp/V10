#!/usr/bin/env python3
"""
Production server startup script
This runs the FastAPI backend for production use
"""
import os
import sys
import uvicorn

# Add the Backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get("PORT", 8006))
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",  # Accept connections from any IP
        port=port,
        # Production settings
        workers=4,  # Multiple workers for handling concurrent users
        log_level="info",
        access_log=True
    )
