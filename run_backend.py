"""
Script to run the FastAPI backend server.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    
    print(f"🚀 Starting FastAPI server on http://{host}:{port}")
    print("📝 API documentation will be available at http://localhost:8000/docs")
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
