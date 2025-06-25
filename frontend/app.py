"""
Streamlit frontend for the AI Calendar Booking Agent.
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
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

# Custom CSS with stronger selectors
st.markdown("""
<style>
    /* Chat message containers */
    .chat-message {
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        margin-bottom: 1rem !important;
        display: flex !important;
        flex-direction: column !important;
        max-width: 80% !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* User messages */
    .user-message {
        background-color: #e3f2fd !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        border: 1px solid #2196f3 !important;
    }

    .user-message * {
        color: #1565c0 !important;
    }

    /* Assistant messages */
    .assistant-message {
        background-color: #f5f5f5 !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        border: 1px solid #ddd !important;
    }

    .assistant-message * {
        color: #333333 !important;
    }

    /* Message headers */
    .message-header {
        font-weight: bold !important;
        margin-bottom: 0.5rem !important;
        font-size: 0.9rem !important;
    }

    .user-header {
        color: #1976d2 !important;
    }

    .assistant-header {
        color: #666666 !important;
    }

    /* Message content */
    .message-content {
        line-height: 1.5 !important;
        white-space: pre-wrap !important;
        font-size: 1rem !important;
    }

    .user-message .message-content {
        color: #1565c0 !important;
    }

    .assistant-message .message-content {
        color: #333333 !important;
    }

    /* Availability slots */
    .availability-slot {
        background-color: #e8f5e8 !important;
        padding: 0.5rem !important;
        border-radius: 0.3rem !important;
        margin: 0.2rem 0 !important;
        border-left: 4px solid #4caf50 !important;
    }

    .availability-slot * {
        color: #2e7d32 !important;
    }

    /* Booking confirmation */
    .booking-confirmed {
        background-color: #e8f5e8 !important;
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        border: 2px solid #4caf50 !important;
        margin: 1rem 0 !important;
    }

    .booking-confirmed * {
        color: #2e7d32 !important;
    }

    /* Override Streamlit's default styling */
    .stMarkdown {
        margin-bottom: 0 !important;
    }

    .stMarkdown p {
        margin-bottom: 0 !important;
    }

    /* Chat container styling */
    .chat-container {
        padding: 1rem 0 !important;
    }

    /* Force text color in all elements */
    .chat-message div, .chat-message span, .chat-message p, .chat-message * {
        color: inherit !important;
    }

    /* Override Streamlit's markdown styling */
    .stMarkdown .chat-message .user-message * {
        color: #1565c0 !important;
    }

    .stMarkdown .chat-message .assistant-message * {
        color: #333333 !important;
    }

    /* Additional overrides for nested elements */
    div[data-testid="stMarkdownContainer"] .user-message * {
        color: #1565c0 !important;
    }

    div[data-testid="stMarkdownContainer"] .assistant-message * {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)


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


def display_message(message: Dict[str, Any], is_user: bool = False):
    """Display a chat message with proper styling."""
    message_class = "user-message" if is_user else "assistant-message"
    header_class = "user-header" if is_user else "assistant-header"
    sender = "You" if is_user else "AI Assistant"
    sender_icon = "👤" if is_user else "🤖"

    content = message.get('content', message.get('response', ''))

    st.markdown(f"""
    <div class="chat-container">
        <div class="chat-message {message_class}">
            <div class="message-header {header_class}">{sender_icon} {sender}</div>
            <div class="message-content">{content}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_availability_slots(slots: List[Dict]):
    """Display available time slots in a formatted way."""
    if not slots:
        return

    st.markdown("""
    <div style="margin: 1rem 0;">
        <h4 style="color: #4caf50; margin-bottom: 0.5rem;">📅 Available Time Slots</h4>
    </div>
    """, unsafe_allow_html=True)

    for i, slot in enumerate(slots[:5]):  # Show max 5 slots
        st.markdown(f"""
        <div class="availability-slot">
            <strong style="color: #2e7d32;">Option {i+1}:</strong>
            <span style="color: #333;">{slot.get('date', 'N/A')} at {slot.get('start_time', 'N/A')} - {slot.get('end_time', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)


def display_booking_confirmation(response_data: Dict[str, Any]):
    """Display booking confirmation details."""
    if response_data.get('booking_confirmed'):
        st.markdown("""
        <div class="booking-confirmed">
            <h3 style="color: #2e7d32; margin-top: 0;">✅ Booking Confirmed!</h3>
            <p style="color: #333; margin-bottom: 0;">Your appointment has been successfully scheduled.</p>
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
        python -m uvicorn backend.main:app --reload --port 8000
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
                    display_message(message, is_user=True)
                else:
                    display_message(message, is_user=False)

                    # Display additional information if available
                    if "available_slots" in message and message["available_slots"]:
                        display_availability_slots(message["available_slots"])

                    if "booking_confirmed" in message:
                        display_booking_confirmation(message)
        else:
            # Show welcome message when no conversation history
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <h3>👋 Welcome to your AI Calendar Assistant!</h3>
                <p>Start by typing a message below, like:</p>
                <ul style="list-style: none; padding: 0;">
                    <li>💬 "Hi, I'd like to schedule a meeting"</li>
                    <li>💬 "Do you have time tomorrow?"</li>
                    <li>💬 "Book a call for next Friday"</li>
                </ul>
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
        
        # Show user message immediately
        with chat_container:
            display_message(user_message, is_user=True)
        
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
