"""
Script to run the Streamlit frontend.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("STREAMLIT_PORT", 8501))
    
    print(f"🎨 Starting Streamlit frontend on http://localhost:{port}")
    
    # Run Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py", 
        "--server.port", str(port),
        "--server.headless", "false"
    ])
