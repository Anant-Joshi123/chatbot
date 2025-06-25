"""
Streamlit frontend with better color control using columns and containers.
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any, List
import uuid

# Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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

def display_user_message(content: str):
    """Display user message with blue styling."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div style="
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #2196f3;
            text-align: left;
        ">
            <div style="color: #1976d2; font-weight: bold; margin-bottom: 0.5rem;">👤 You</div>
            <div style="color: #1565c0; line-height: 1.5;">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def display_assistant_message(content: str):
    """Display assistant message with gray styling."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div style="
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #666;
            text-align: left;
        ">
            <div style="color: #666; font-weight: bold; margin-bottom: 0.5rem;">🤖 AI Assistant</div>
            <div style="color: #333; line-height: 1.5; white-space: pre-wrap;">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def display_availability_slots(slots: List[Dict]):
    """Display available time slots."""
    if not slots:
        return
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="
            background-color: #e8f5e8;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #4caf50;
        ">
            <div style="color: #2e7d32; font-weight: bold; margin-bottom: 0.5rem;">📅 Available Time Slots</div>
        """, unsafe_allow_html=True)
        
        for i, slot in enumerate(slots[:5], 1):
            st.markdown(f"""
            <div style="
                background-color: #ffffff;
                padding: 0.5rem;
                border-radius: 5px;
                margin: 0.3rem 0;
                border: 1px solid #c8e6c9;
            ">
                <span style="color: #2e7d32; font-weight: bold;">Option {i}:</span>
                <span style="color: #333;"> {slot.get('date', 'N/A')} from {slot.get('start_time', 'N/A')} to {slot.get('end_time', 'N/A')}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_booking_confirmation():
    """Display booking confirmation."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="
            background-color: #e8f5e8;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 2px solid #4caf50;
            text-align: center;
        ">
            <div style="color: #2e7d32; font-size: 1.2rem; font-weight: bold;">✅ Booking Confirmed!</div>
            <div style="color: #333; margin-top: 0.5rem;">Your appointment has been successfully scheduled.</div>
        </div>
        """, unsafe_allow_html=True)

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
    3. **Provide details** when asked
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
    
    # Chat container
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        if st.session_state.messages:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    display_user_message(message["content"])
                else:
                    display_assistant_message(message["content"])
                    
                    # Display additional information if available
                    if "available_slots" in message and message["available_slots"]:
                        display_availability_slots(message["available_slots"])
                    
                    if "booking_confirmed" in message and message["booking_confirmed"]:
                        display_booking_confirmation()
        else:
            # Show welcome message
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; color: #666; border: 2px dashed #ddd; border-radius: 10px;">
                    <h3 style="color: #333;">👋 Welcome to your AI Calendar Assistant!</h3>
                    <p style="color: #666;">Start by typing a message below, like:</p>
                    <div style="text-align: left; margin: 1rem 0;">
                        <div style="margin: 0.5rem 0; color: #2196f3;">💬 "Hi, I'd like to schedule a meeting"</div>
                        <div style="margin: 0.5rem 0; color: #2196f3;">💬 "Do you have time tomorrow?"</div>
                        <div style="margin: 0.5rem 0; color: #2196f3;">💬 "Book a call for next Friday"</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
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
        
        # Rerun to show the new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        AI Calendar Booking Agent | Built with FastAPI, LangGraph & Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
