"""
Test script for the AI Calendar Booking Agent.
Tests various conversation scenarios and edge cases.
"""

import os
import sys
import asyncio
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

API_BASE_URL = "http://localhost:8000"

class AgentTester:
    """Test class for the booking agent."""
    
    def __init__(self):
        self.session_id = "test_session_" + str(int(datetime.now().timestamp()))
        self.conversation_history = []
    
    def check_api_status(self) -> bool:
        """Check if the API is running."""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the agent."""
        try:
            payload = {
                "message": message,
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.conversation_history.append({
                    "user": message,
                    "agent": result.get("response", ""),
                    "intent": result.get("intent"),
                    "extracted_info": result.get("extracted_info"),
                    "available_slots": result.get("available_slots"),
                    "booking_confirmed": result.get("booking_confirmed", False)
                })
                return result
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return {}
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            return {}
    
    def print_conversation_step(self, user_msg: str, agent_response: Dict[str, Any]):
        """Print a conversation step."""
        print(f"\n👤 User: {user_msg}")
        print(f"🤖 Agent: {agent_response.get('response', 'No response')}")
        
        if agent_response.get('intent'):
            print(f"🎯 Intent: {agent_response['intent']}")
        
        if agent_response.get('extracted_info'):
            print(f"📝 Extracted: {json.dumps(agent_response['extracted_info'], indent=2)}")
        
        if agent_response.get('available_slots'):
            print(f"📅 Available slots: {len(agent_response['available_slots'])} found")
        
        if agent_response.get('booking_confirmed'):
            print("✅ Booking confirmed!")
        
        print("-" * 60)
    
    def test_basic_greeting(self):
        """Test basic greeting scenario."""
        print("\n🧪 Testing Basic Greeting...")
        
        test_messages = [
            "Hello",
            "Hi there",
            "Good morning"
        ]
        
        for msg in test_messages:
            response = self.send_message(msg)
            self.print_conversation_step(msg, response)
            
            # Check if response is appropriate
            if "help" in response.get("response", "").lower():
                print("✅ Greeting test passed")
            else:
                print("⚠️  Greeting response could be improved")
    
    def test_booking_scenarios(self):
        """Test various booking scenarios."""
        print("\n🧪 Testing Booking Scenarios...")
        
        scenarios = [
            "I want to schedule a meeting",
            "Do you have any free time tomorrow?",
            "Book a call for next Friday at 2 PM",
            "I need to schedule a 30-minute meeting for next week",
            "Can we meet sometime this afternoon?",
            "Schedule a team meeting for Monday morning"
        ]
        
        for scenario in scenarios:
            print(f"\n📋 Scenario: {scenario}")
            response = self.send_message(scenario)
            self.print_conversation_step(scenario, response)
            
            # Reset session for next scenario
            self.session_id = "test_session_" + str(int(datetime.now().timestamp()))
    
    def test_conversation_flow(self):
        """Test a complete conversation flow."""
        print("\n🧪 Testing Complete Conversation Flow...")
        
        conversation_steps = [
            "Hi, I'd like to schedule a meeting",
            "Tomorrow afternoon would be great",
            "Let's make it a 1-hour meeting",
            "The first option looks good",
            "Yes, please book it"
        ]
        
        for step in conversation_steps:
            response = self.send_message(step)
            self.print_conversation_step(step, response)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("\n🧪 Testing Edge Cases...")
        
        edge_cases = [
            "",  # Empty message
            "What's the weather like?",  # Unrelated question
            "Book a meeting for yesterday",  # Past date
            "Schedule something for 25:00",  # Invalid time
            "I want to cancel everything",  # Cancellation request
            "Book 50 meetings for tomorrow",  # Unrealistic request
        ]
        
        for case in edge_cases:
            print(f"\n🔍 Edge case: '{case}'")
            response = self.send_message(case)
            self.print_conversation_step(case, response)
            
            # Reset session for next case
            self.session_id = "test_session_" + str(int(datetime.now().timestamp()))
    
    def test_api_endpoints(self):
        """Test direct API endpoints."""
        print("\n🧪 Testing API Endpoints...")
        
        # Test health endpoint
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
        
        # Test availability endpoint
        try:
            payload = {
                "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "duration_minutes": 60
            }
            response = requests.post(f"{API_BASE_URL}/availability", json=payload)
            if response.status_code == 200:
                result = response.json()
                print("✅ Availability endpoint working")
                print(f"   Found {len(result.get('available_slots', []))} slots")
            else:
                print(f"❌ Availability endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Availability endpoint error: {e}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting AI Calendar Booking Agent Tests")
        print("=" * 60)
        
        # Check if API is running
        if not self.check_api_status():
            print("❌ API is not running! Please start the backend server first.")
            print("   Run: python run_backend.py")
            return
        
        print("✅ API is running")
        
        # Run tests
        try:
            self.test_basic_greeting()
            self.test_booking_scenarios()
            self.test_conversation_flow()
            self.test_edge_cases()
            self.test_api_endpoints()
            
            print("\n" + "=" * 60)
            print("🎉 All tests completed!")
            print(f"📊 Total conversations tested: {len(self.conversation_history)}")
            
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
    
    def print_summary(self):
        """Print test summary."""
        if not self.conversation_history:
            return
        
        print("\n📋 Test Summary:")
        print(f"   Total interactions: {len(self.conversation_history)}")
        
        intents = [conv.get('intent') for conv in self.conversation_history if conv.get('intent')]
        if intents:
            print(f"   Detected intents: {set(intents)}")
        
        bookings_confirmed = sum(1 for conv in self.conversation_history if conv.get('booking_confirmed'))
        if bookings_confirmed:
            print(f"   Bookings confirmed: {bookings_confirmed}")


def main():
    """Main test function."""
    tester = AgentTester()
    tester.run_all_tests()
    tester.print_summary()


if __name__ == "__main__":
    main()
