"""
Startup script for the AI Calendar Booking Agent.
Starts both backend and frontend services.
"""

import os
import sys
import time
import subprocess
import threading
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AppLauncher:
    """Application launcher for both backend and frontend."""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
    
    def check_requirements(self):
        """Check if all requirements are met."""
        print("🔍 Checking requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("⚠️  .env file not found. Creating from template...")
            if os.path.exists('.env.example'):
                with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                    dst.write(src.read())
                print("✅ .env file created. Please edit it with your API keys.")
            else:
                print("❌ .env.example not found")
                return False
        
        # Check OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key or openai_key == 'your_openai_api_key_here':
            print("❌ OpenAI API key not set in .env file")
            print("   Please add your OpenAI API key to the .env file")
            return False
        
        # Check Google Calendar credentials
        if not os.path.exists('credentials.json'):
            print("⚠️  Google Calendar credentials.json not found")
            print("   The app will work but calendar integration may fail")
            print("   Please add credentials.json for full functionality")
        
        print("✅ Requirements check passed")
        return True
    
    def start_backend(self):
        """Start the FastAPI backend."""
        print("🚀 Starting backend server...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "run_backend.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started successfully")
                return True
            else:
                print("❌ Backend server failed to start")
                stdout, stderr = self.backend_process.communicate()
                print(f"Error: {stderr}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend."""
        print("🎨 Starting frontend interface...")
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, "run_frontend.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend interface started successfully")
                return True
            else:
                print("❌ Frontend interface failed to start")
                stdout, stderr = self.frontend_process.communicate()
                print(f"Error: {stderr}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor running processes."""
        while self.running:
            time.sleep(5)
            
            # Check backend
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️  Backend process stopped unexpectedly")
                break
            
            # Check frontend
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️  Frontend process stopped unexpectedly")
                break
    
    def stop_services(self):
        """Stop all services."""
        print("\n🛑 Stopping services...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("🔪 Backend force killed")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("🔪 Frontend force killed")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\n📡 Received signal {signum}")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Main run method."""
        print("🤖 AI CALENDAR BOOKING AGENT")
        print("=" * 50)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check requirements
        if not self.check_requirements():
            print("\n❌ Requirements check failed. Please fix the issues above.")
            return
        
        try:
            # Start backend
            if not self.start_backend():
                print("❌ Failed to start backend. Exiting.")
                return
            
            # Start frontend
            if not self.start_frontend():
                print("❌ Failed to start frontend. Stopping backend.")
                self.stop_services()
                return
            
            # Show success message
            print("\n" + "=" * 50)
            print("🎉 APPLICATION STARTED SUCCESSFULLY!")
            print("=" * 50)
            print("🌐 Access the application at:")
            print(f"   Frontend UI: http://localhost:{os.getenv('STREAMLIT_PORT', 8501)}")
            print(f"   Backend API: http://localhost:{os.getenv('FASTAPI_PORT', 8000)}")
            print(f"   API Docs: http://localhost:{os.getenv('FASTAPI_PORT', 8000)}/docs")
            print("\n💡 Usage:")
            print("   1. Open the frontend URL in your browser")
            print("   2. Start chatting with the AI agent")
            print("   3. Ask to schedule meetings naturally")
            print("\n⏹️  Press Ctrl+C to stop the application")
            print("=" * 50)
            
            # Monitor processes
            monitor_thread = threading.Thread(target=self.monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⏹️  Application interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.stop_services()

def main():
    """Main function."""
    launcher = AppLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
