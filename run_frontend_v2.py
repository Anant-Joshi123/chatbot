"""
Script to run the alternative Streamlit frontend with better chat styling.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("STREAMLIT_PORT", 8501))
    
    print(f"🎨 Starting Streamlit frontend (v2) on http://localhost:{port}")
    
    # Run Streamlit with the alternative app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app_v2.py", 
        "--server.port", str(port),
        "--server.headless", "false"
    ])
