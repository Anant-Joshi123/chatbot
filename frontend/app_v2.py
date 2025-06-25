"""
Alternative Streamlit frontend using built-in chat elements.
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any, List
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="AI Calendar Booking Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_status" not in st.session_state:
        st.session_state.api_status = check_api_status()

def check_api_status() -> bool:
    """Check if the FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def send_message(message: str) -> Dict[str, Any]:
    """Send message to the booking agent API."""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Error: {response.status_code} - {response.text}",
                "session_id": st.session_state.session_id,
                "error": True
            }
    
    except requests.exceptions.RequestException as e:
        return {
            "response": f"Connection error: {str(e)}",
            "session_id": st.session_state.session_id,
            "error": True
        }

def display_availability_slots(slots: List[Dict]):
    """Display available time slots."""
    if not slots:
        return
    
    st.success("📅 **Available Time Slots:**")
    
    for i, slot in enumerate(slots[:5], 1):
        st.info(f"**Option {i}:** {slot.get('date', 'N/A')} from {slot.get('start_time', 'N/A')} to {slot.get('end_time', 'N/A')}")

def display_booking_confirmation():
    """Display booking confirmation."""
    st.success("✅ **Booking Confirmed!** Your appointment has been successfully scheduled.")

def sidebar_info():
    """Display information in the sidebar."""
    st.sidebar.title("📅 AI Booking Agent")
    
    # API Status
    status_color = "🟢" if st.session_state.api_status else "🔴"
    status_text = "Connected" if st.session_state.api_status else "Disconnected"
    st.sidebar.markdown(f"**API Status:** {status_color} {status_text}")
    
    # Session Info
    st.sidebar.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    st.sidebar.markdown(f"**Messages:** {len(st.session_state.messages)}")
    
    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 How to Use")
    st.sidebar.markdown("""
    1. **Start a conversation** by typing a greeting
    2. **Request a meeting** by saying something like:
       - "I want to schedule a meeting"
       - "Book a call for tomorrow"
       - "Do you have time this Friday?"
    3. **Provide details** when asked:
       - Date and time preferences
       - Meeting duration
       - Meeting purpose
    4. **Confirm** when shown available slots
    """)
    
    # Example messages
    st.sidebar.markdown("### 📝 Example Messages")
    example_messages = [
        "Hi, I'd like to schedule a meeting",
        "Do you have any free time tomorrow afternoon?",
        "Book a 30-minute call for next Friday",
        "I need to schedule a team meeting for next week"
    ]
    
    for example in example_messages:
        if st.sidebar.button(f"💬 {example}", key=f"example_{hash(example)}"):
            st.session_state.example_message = example
    
    # Clear conversation
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    # Refresh API status
    if st.sidebar.button("🔄 Refresh API Status"):
        st.session_state.api_status = check_api_status()
        st.rerun()

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Sidebar
    sidebar_info()
    
    # Main content
    st.title("🤖 AI Calendar Booking Agent")
    st.markdown("Welcome! I'm your AI assistant for booking calendar appointments. How can I help you today?")
    
    # API Status Warning
    if not st.session_state.api_status:
        st.error("""
        ⚠️ **Backend API is not running!**
        
        Please start the FastAPI backend server:
        ```bash
        python run_backend.py
        ```
        """)
        st.stop()
    
    # Display conversation history using Streamlit's chat elements
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                # Display additional information if available
                if "available_slots" in message and message["available_slots"]:
                    display_availability_slots(message["available_slots"])
                
                if "booking_confirmed" in message and message["booking_confirmed"]:
                    display_booking_confirmation()
    
    # Handle example message from sidebar
    if "example_message" in st.session_state:
        user_input = st.session_state.example_message
        del st.session_state.example_message
    else:
        user_input = st.chat_input("Type your message here...")
    
    # Process user input
    if user_input:
        # Add user message to history
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Send to API and get response
        with st.spinner("🤔 Thinking..."):
            response_data = send_message(user_input)
        
        # Add assistant response to history
        assistant_message = {
            "role": "assistant",
            "content": response_data.get("response", "Sorry, I couldn't process that."),
            "timestamp": datetime.now().isoformat(),
            "available_slots": response_data.get("available_slots"),
            "booking_confirmed": response_data.get("booking_confirmed", False),
            "intent": response_data.get("intent"),
            "extracted_info": response_data.get("extracted_info")
        }
        st.session_state.messages.append(assistant_message)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response_data.get("response", "Sorry, I couldn't process that."))
            
            # Display additional information if available
            if response_data.get("available_slots"):
                display_availability_slots(response_data["available_slots"])
            
            if response_data.get("booking_confirmed"):
                display_booking_confirmation()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        AI Calendar Booking Agent | Built with FastAPI, LangGraph & Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
