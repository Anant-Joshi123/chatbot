"""
Quick test to verify the booking agent is working.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_conversation():
    """Test a complete booking conversation."""
    print("🧪 Testing AI Calendar Booking Agent")
    print("=" * 50)
    
    session_id = "test_session_123"
    
    # Test conversation flow
    conversation = [
        "Hello, I'd like to schedule a meeting",
        "Tomorrow afternoon would be great",
        "The first option looks good",
        "Yes, please confirm the booking"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n👤 Step {i}: {message}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={"message": message, "session_id": session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Agent: {data['response']}")
                
                if data.get('available_slots'):
                    print(f"📅 Found {len(data['available_slots'])} available slots")
                
                if data.get('booking_confirmed'):
                    print("✅ Booking confirmed!")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("🌐 Frontend available at: http://localhost:8501")
    print("📚 API docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    test_conversation()
