"""
Script to run the colored Streamlit frontend.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("STREAMLIT_PORT", 8501))
    
    print(f"🎨 Starting Streamlit frontend (colored version) on http://localhost:{port}")
    
    # Run Streamlit with the colored app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app_colored.py", 
        "--server.port", str(port),
        "--server.headless", "false"
    ])
