"""
Demo script for the AI Calendar Booking Agent.
Shows example conversations and capabilities.
"""

import os
import sys
import time
import requests
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

API_BASE_URL = "http://localhost:8000"

def check_api_status():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def send_message(message: str, session_id: str = "demo_session"):
    """Send a message to the agent."""
    try:
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"Error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"response": f"Connection error: {e}"}

def print_conversation_step(user_msg: str, agent_response: dict, delay: float = 1.0):
    """Print a conversation step with typing effect."""
    print(f"\n👤 You: {user_msg}")
    time.sleep(delay)
    
    response_text = agent_response.get("response", "No response")
    print(f"🤖 AI Assistant: {response_text}")
    
    # Show additional info if available
    if agent_response.get("available_slots"):
        slots = agent_response["available_slots"][:3]  # Show first 3 slots
        print(f"📅 Found {len(agent_response['available_slots'])} available slots")
    
    if agent_response.get("booking_confirmed"):
        print("✅ Booking confirmed!")
    
    time.sleep(delay * 1.5)

def demo_conversation_1():
    """Demo: Basic booking conversation."""
    print("\n" + "="*60)
    print("🎬 DEMO 1: Basic Meeting Booking")
    print("="*60)
    
    session_id = f"demo1_{int(datetime.now().timestamp())}"
    
    conversation = [
        "Hello, I'd like to schedule a meeting",
        "Tomorrow afternoon would be perfect",
        "Let's make it a 1-hour meeting about project planning",
        "The first option looks good to me",
        "Yes, please book it!"
    ]
    
    for message in conversation:
        response = send_message(message, session_id)
        print_conversation_step(message, response)

def demo_conversation_2():
    """Demo: Quick booking with specific time."""
    print("\n" + "="*60)
    print("🎬 DEMO 2: Quick Booking with Specific Time")
    print("="*60)
    
    session_id = f"demo2_{int(datetime.now().timestamp())}"
    
    conversation = [
        "Hi! Can you book a call for next Friday at 2 PM?",
        "Make it a 30-minute client consultation",
        "Perfect, let's confirm that slot"
    ]
    
    for message in conversation:
        response = send_message(message, session_id)
        print_conversation_step(message, response)

def demo_conversation_3():
    """Demo: Availability checking."""
    print("\n" + "="*60)
    print("🎬 DEMO 3: Checking Availability")
    print("="*60)
    
    session_id = f"demo3_{int(datetime.now().timestamp())}"
    
    conversation = [
        "Do you have any free time this week?",
        "I need about 45 minutes for a team meeting",
        "Wednesday looks good, what times are available?",
        "The 10 AM slot works perfectly"
    ]
    
    for message in conversation:
        response = send_message(message, session_id)
        print_conversation_step(message, response)

def demo_edge_cases():
    """Demo: Edge cases and error handling."""
    print("\n" + "="*60)
    print("🎬 DEMO 4: Edge Cases & Error Handling")
    print("="*60)
    
    edge_cases = [
        ("Unrelated question", "What's the weather like today?"),
        ("Past date request", "Can you book something for yesterday?"),
        ("Vague request", "I need to meet someone sometime"),
        ("Cancellation", "Actually, never mind, cancel that"),
    ]
    
    for case_name, message in edge_cases:
        print(f"\n🔍 Testing: {case_name}")
        session_id = f"demo_edge_{int(datetime.now().timestamp())}"
        response = send_message(message, session_id)
        print_conversation_step(message, response, delay=0.5)

def show_api_info():
    """Show API information."""
    print("\n" + "="*60)
    print("📊 API INFORMATION")
    print("="*60)
    
    try:
        # Health check
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Backend Status: Healthy")
            print(f"   Timestamp: {health_data.get('timestamp', 'N/A')}")
            print(f"   Services: {health_data.get('services', {})}")
        
        # Check availability endpoint
        from datetime import timedelta
        availability_payload = {
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "duration_minutes": 60
        }
        
        availability_response = requests.post(
            f"{API_BASE_URL}/availability", 
            json=availability_payload
        )
        
        if availability_response.status_code == 200:
            availability_data = availability_response.json()
            slots_count = len(availability_data.get('available_slots', []))
            print(f"📅 Available Slots: {slots_count} found for next week")
        
    except Exception as e:
        print(f"❌ Error checking API: {e}")

def main():
    """Main demo function."""
    print("🚀 AI CALENDAR BOOKING AGENT - DEMO")
    print("🤖 Showcasing conversational booking capabilities")
    print("⏰ " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Check if API is running
    if not check_api_status():
        print("\n❌ Backend API is not running!")
        print("Please start the backend server first:")
        print("   python run_backend.py")
        return
    
    print("\n✅ Backend API is running")
    
    try:
        # Show API info
        show_api_info()
        
        # Run demo conversations
        demo_conversation_1()
        demo_conversation_2()
        demo_conversation_3()
        demo_edge_cases()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETED!")
        print("="*60)
        print("💡 Key Features Demonstrated:")
        print("   ✅ Natural language understanding")
        print("   ✅ Context-aware conversations")
        print("   ✅ Calendar availability checking")
        print("   ✅ Booking confirmation flow")
        print("   ✅ Edge case handling")
        print("\n🌐 Try the full interface at: http://localhost:8501")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()
