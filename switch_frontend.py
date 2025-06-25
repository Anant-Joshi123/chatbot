"""
Script to switch between different frontend versions.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_menu():
    """Show frontend options menu."""
    print("🎨 AI Calendar Booking Agent - Frontend Options")
    print("=" * 50)
    print("1. Original Frontend (app.py) - Custom CSS styling")
    print("2. Colored Frontend (app_colored.py) - Column-based styling")
    print("3. Chat Frontend (app_v2.py) - Streamlit chat elements")
    print("4. Exit")
    print("=" * 50)

def run_frontend(app_file: str, description: str):
    """Run a specific frontend version."""
    port = int(os.getenv("STREAMLIT_PORT", 8501))
    
    print(f"🚀 Starting {description} on http://localhost:{port}")
    print("Press Ctrl+C to stop and return to menu")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            f"frontend/{app_file}", 
            "--server.port", str(port),
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Frontend stopped")

def main():
    """Main menu function."""
    while True:
        show_menu()
        
        try:
            choice = input("Select an option (1-4): ").strip()
            
            if choice == "1":
                run_frontend("app.py", "Original Frontend")
            elif choice == "2":
                run_frontend("app_colored.py", "Colored Frontend")
            elif choice == "3":
                run_frontend("app_v2.py", "Chat Frontend")
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
