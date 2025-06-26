"""
Test script for the standalone Streamlit app conversation logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the MockBackend class from streamlit_app
from streamlit_app import MockBackend

def test_conversation():
    """Test the conversation flow."""
    print("🧪 Testing Standalone App Conversation Logic")
    print("=" * 60)
    
    # Initialize mock backend
    backend = MockBackend()
    session_id = "test_session"
    
    # Test conversation flow
    test_messages = [
        "Hello, I'd like to schedule a meeting",
        "Tomorrow afternoon would be great", 
        "The first option looks good",
        "Yes, please confirm the booking"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n👤 Step {i}: {message}")
        
        # Process message
        response = backend.process_chat(message, session_id)
        
        print(f"🤖 Response: {response['response']}")
        print(f"🎯 Intent: {response['intent']}")
        print(f"📝 Extracted: {response['extracted_info']}")
        
        if response.get('available_slots'):
            print(f"📅 Available slots: {len(response['available_slots'])}")
            for j, slot in enumerate(response['available_slots'][:2], 1):
                print(f"   {j}. {slot['date']} {slot['start_time']}-{slot['end_time']}")
        
        if response.get('booking_confirmed'):
            print("✅ Booking confirmed!")
        
        print("-" * 40)
    
    print("\n🎉 Test completed!")

def test_edge_cases():
    """Test edge cases."""
    print("\n🔍 Testing Edge Cases")
    print("=" * 60)
    
    backend = MockBackend()
    
    edge_cases = [
        ("Empty message", ""),
        ("Just greeting", "Hi"),
        ("Vague request", "I need help"),
        ("Specific request", "Book a meeting for tomorrow at 2 PM"),
        ("Selection without context", "Option 1"),
    ]
    
    for case_name, message in edge_cases:
        print(f"\n🔍 {case_name}: '{message}'")
        response = backend.process_chat(message, f"test_{case_name}")
        print(f"🤖 Response: {response['response'][:100]}...")
        print(f"🎯 Intent: {response['intent']}")

if __name__ == "__main__":
    test_conversation()
    test_edge_cases()
