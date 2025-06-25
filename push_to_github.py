"""
Script to help push to GitHub with proper authentication.
"""

import subprocess
import sys
import os

def push_to_github():
    """Push code to GitHub with authentication guidance."""
    
    print("🚀 GitHub Push Helper")
    print("=" * 50)
    
    print("❌ Permission denied error detected!")
    print("This happens when:")
    print("1. You're logged in with a different GitHub account")
    print("2. You need to authenticate with a Personal Access Token")
    print("3. The repository doesn't exist or you don't have access")
    
    print("\n🔧 SOLUTIONS:")
    print("\n1. **Use Personal Access Token (Recommended):**")
    print("   a. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("   b. Generate new token with 'repo' permissions")
    print("   c. Use this command:")
    print("   git remote set-url origin https://YOUR_TOKEN@github.com/Anant-Joshi123/chatbot.git")
    print("   d. Then: git push -u origin master")
    
    print("\n2. **Use SSH (Alternative):**")
    print("   a. Set up SSH key in GitHub")
    print("   b. Change remote URL:")
    print("   git remote set-url origin git@github.com:Anant-Joshi123/chatbot.git")
    print("   c. Then: git push -u origin master")
    
    print("\n3. **Create New Repository:**")
    print("   a. Go to github.com/Anant-Joshi123")
    print("   b. Create new repository named 'chatbot'")
    print("   c. Make sure it's public")
    print("   d. Don't initialize with README (we already have files)")
    
    print("\n4. **Check Repository Access:**")
    print("   a. Make sure you're logged into the correct GitHub account")
    print("   b. Verify the repository exists: https://github.com/Anant-Joshi123/chatbot")
    print("   c. Check if you have write permissions")
    
    print("\n" + "=" * 50)
    print("📋 CURRENT STATUS:")
    
    # Check current remote
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, cwd='.')
        print("Current remote URLs:")
        print(result.stdout)
    except Exception as e:
        print(f"Error checking remotes: {e}")
    
    # Check current branch
    try:
        result = subprocess.run(['git', 'branch'], 
                              capture_output=True, text=True, cwd='.')
        print("Current branch:")
        print(result.stdout)
    except Exception as e:
        print(f"Error checking branch: {e}")
    
    print("\n🎯 QUICK FIX:")
    print("1. Get your Personal Access Token from GitHub")
    print("2. Run this command (replace YOUR_TOKEN):")
    print("   git remote set-url origin https://YOUR_TOKEN@github.com/Anant-Joshi123/chatbot.git")
    print("3. Then run: git push -u origin master")
    
    print("\n💡 Need help getting a token?")
    print("Go to: https://github.com/settings/tokens")

if __name__ == "__main__":
    push_to_github()
