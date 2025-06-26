"""
Main Streamlit app for deployment to Streamlit Cloud.
This is a standalone version that works without the FastAPI backend.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid
import random

# Try to import pytz, fallback if not available
try:
    import pytz
except ImportError:
    # Create a simple timezone class for fallback
    class SimpleTimezone:
        def __init__(self, name):
            self.name = name
        def localize(self, dt):
            return dt
    pytz = type('pytz', (), {'timezone': lambda name: SimpleTimezone(name)})()

# Force standalone mode - no external API calls
STANDALONE_MODE = True

# Page configuration
st.set_page_config(
    page_title="AI Calendar Booking Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mock Backend for Streamlit Cloud
class MockBackend:
    """Mock backend that simulates the FastAPI responses for Streamlit Cloud."""
    
    def __init__(self):
        self.sessions = {}
        self.timezone = pytz.timezone('America/New_York')
    
    def process_chat(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process chat message and return mock response."""
        
        # Initialize session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'step': 'greeting',
                'extracted_info': {},
                'available_slots': [],
                'selected_slot': None
            }
        
        session = self.sessions[session_id]
        message_lower = message.lower().strip()
        
        # Simple intent analysis
        intent = self._analyze_intent(message_lower)
        
        # Extract information
        extracted_info = self._extract_info(message)
        session['extracted_info'].update(extracted_info)

        # Debug info (can be removed in production)
        debug_info = f"Intent: {intent}, Step: {session['step']}, Extracted: {extracted_info}"
        
        # Generate response based on intent and current step
        if intent == 'greeting' and session['step'] == 'greeting':
            response = "Hello! I'm your AI calendar assistant. I can help you schedule meetings and check your availability. What would you like to do today?"
            session['step'] = 'collecting_info'

        elif intent == 'book_meeting' or (session['step'] == 'collecting_info' and intent != 'general'):
            response = self._handle_booking_request(session)
            if session.get('available_slots'):
                session['step'] = 'showing_slots'

        elif intent == 'select_slot' or (session['step'] == 'showing_slots' and intent != 'confirm_booking'):
            response = self._handle_slot_selection(session, message)
            if session.get('selected_slot'):
                session['step'] = 'confirming'

        elif intent == 'confirm_booking' or (session['step'] == 'confirming'):
            response = self._handle_confirmation(session, message_lower)

        elif session['step'] == 'collecting_info':
            # If we're collecting info but didn't get booking intent, try to extract info anyway
            response = self._handle_booking_request(session)
            if session.get('available_slots'):
                session['step'] = 'showing_slots'

        else:
            response = "I'm here to help you schedule meetings and manage your calendar. You can ask me to 'schedule a meeting', 'check availability', or 'book an appointment'. How can I assist you today?"
            session['step'] = 'collecting_info'
        
        return {
            "response": response,
            "session_id": session_id,
            "intent": intent,
            "extracted_info": session['extracted_info'],
            "available_slots": session.get('available_slots', []),
            "booking_confirmed": session.get('booking_confirmed', False)
        }
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze user intent."""
        greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings']
        booking_words = ['schedule', 'book', 'meeting', 'appointment', 'call', 'time', 'available', 'free', 'slot']
        confirmation_words = ['yes', 'confirm', 'ok', 'sure', 'sounds good', 'perfect', 'please']
        selection_words = ['first', 'second', 'third', 'option', '1', '2', '3', 'looks good', 'good', 'that one']

        # More flexible intent detection
        if any(word in message for word in greeting_words) and len(message.split()) <= 5:
            return 'greeting'
        elif any(word in message for word in confirmation_words) and ('book' in message or 'confirm' in message or 'yes' in message):
            return 'confirm_booking'
        elif any(word in message for word in selection_words):
            return 'select_slot'
        elif any(word in message for word in booking_words) or 'want' in message or 'need' in message or 'like' in message:
            return 'book_meeting'
        else:
            return 'general'
    
    def _extract_info(self, message: str) -> Dict[str, Any]:
        """Extract booking information."""
        info = {}
        message_lower = message.lower()
        
        # Extract dates
        if 'tomorrow' in message_lower:
            tomorrow = datetime.now(self.timezone) + timedelta(days=1)
            info['date'] = tomorrow.strftime('%Y-%m-%d')
        elif 'friday' in message_lower:
            today = datetime.now(self.timezone)
            days_ahead = 4 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            friday = today + timedelta(days=days_ahead)
            info['date'] = friday.strftime('%Y-%m-%d')
        elif 'next week' in message_lower:
            next_week = datetime.now(self.timezone) + timedelta(days=7)
            info['date'] = next_week.strftime('%Y-%m-%d')
        
        # Extract duration
        if '30' in message and 'minute' in message_lower:
            info['duration'] = 30
        elif '1 hour' in message_lower:
            info['duration'] = 60
        
        return info
    
    def _handle_booking_request(self, session: Dict) -> str:
        """Handle booking requests."""
        extracted = session['extracted_info']

        # If no date specified, ask for it
        if not extracted.get('date'):
            return "I'd be happy to help you schedule a meeting! Could you please tell me your preferred date? For example, you could say 'tomorrow', 'next Friday', or a specific date."

        # Generate mock available slots
        available_slots = self._generate_mock_slots(extracted.get('date'))
        session['available_slots'] = available_slots

        if not available_slots:
            return "I couldn't find any available slots for your requested time. Could you try a different date?"

        # Create a more natural response
        date_str = extracted.get('date')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%A, %B %d')
        except:
            formatted_date = date_str

        response = f"Perfect! I found some available time slots for {formatted_date}:\n\n"
        for i, slot in enumerate(available_slots[:3], 1):
            response += f"{i}. {slot['start_time']} - {slot['end_time']}\n"

        response += "\nWhich time works best for you? Just let me know the number (1, 2, or 3) or say something like 'the first option looks good'."
        return response
    
    def _generate_mock_slots(self, date_str: str) -> List[Dict]:
        """Generate mock available slots."""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            date_obj = datetime.now(self.timezone) + timedelta(days=1)
        
        slots = []
        times = ['09:00 AM', '11:00 AM', '02:00 PM', '03:30 PM', '04:00 PM']
        
        for i, time in enumerate(times[:3]):
            start_time = datetime.strptime(f"{date_obj.strftime('%Y-%m-%d')} {time}", '%Y-%m-%d %I:%M %p')
            end_time = start_time + timedelta(hours=1)
            
            slots.append({
                'date': date_obj.strftime('%Y-%m-%d'),
                'start_time': start_time.strftime('%I:%M %p'),
                'end_time': end_time.strftime('%I:%M %p'),
                'start': start_time,
                'end': end_time
            })
        
        return slots
    
    def _handle_slot_selection(self, session: Dict, message: str) -> str:
        """Handle slot selection."""
        available_slots = session.get('available_slots', [])
        if not available_slots:
            return "I don't see any available slots to choose from."
        
        message_lower = message.lower()
        selected_index = None
        
        if 'first' in message_lower or '1' in message or 'option 1' in message_lower:
            selected_index = 0
        elif 'second' in message_lower or '2' in message:
            selected_index = 1
        elif 'third' in message_lower or '3' in message:
            selected_index = 2
        elif 'looks good' in message_lower or 'good' in message_lower:
            selected_index = 0
        
        if selected_index is not None and selected_index < len(available_slots):
            session['selected_slot'] = available_slots[selected_index]
            return f"Perfect! I'll book the slot on {available_slots[selected_index]['date']} from {available_slots[selected_index]['start_time']} to {available_slots[selected_index]['end_time']}. Should I confirm this booking?"
        else:
            return "I'm not sure which slot you'd like to select. Could you please specify 'option 1', 'option 2', etc.?"
    
    def _handle_confirmation(self, session: Dict, message: str) -> str:
        """Handle booking confirmation."""
        if 'yes' in message or 'confirm' in message or 'ok' in message:
            selected_slot = session.get('selected_slot')
            if selected_slot:
                session['booking_confirmed'] = True
                event_id = f"mock_{random.randint(1000, 9999)}"
                
                return f"""✅ **Booking Confirmed!**

Your meeting has been successfully scheduled:
📅 **Date:** {selected_slot['date']}
🕐 **Time:** {selected_slot['start_time']} - {selected_slot['end_time']}
📝 **Event ID:** {event_id}

This is a demo booking using mock calendar data. In the full version with backend deployment, this would create a real calendar event.

Is there anything else I can help you with?"""
            else:
                return "I don't see a selected time slot to confirm. Please choose a time slot first."
        else:
            return "No problem! Would you like to see different time options?"

# Initialize mock backend
if 'mock_backend' not in st.session_state:
    st.session_state.mock_backend = MockBackend()

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Title and description
    st.title("🤖 AI Calendar Booking Agent")
    st.markdown("Welcome! I'm your AI assistant for booking calendar appointments. How can I help you today?")
    
    # Info about demo mode
    st.info("🔄 **Demo Mode:** This is running with a mock backend. For full functionality with real calendar integration, deploy the complete FastAPI + Streamlit stack.")
    
    # Sidebar
    with st.sidebar:
        st.title("📅 AI Booking Agent")
        st.markdown("**Status:** 🟢 Demo Mode Active")
        st.markdown(f"**Session:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")
        
        st.markdown("---")
        st.markdown("### 💡 How to Use")
        st.markdown("""
        1. **Start a conversation** by typing a greeting
        2. **Request a meeting** by saying something like:
           - "I want to schedule a meeting"
           - "Book a call for tomorrow"
           - "Do you have time this Friday?"
        3. **Provide details** when asked
        4. **Confirm** when shown available slots
        """)
        
        st.markdown("### 📝 Example Messages")
        example_messages = [
            "Hi, I'd like to schedule a meeting",
            "Do you have any free time tomorrow afternoon?",
            "Book a 30-minute call for next Friday",
            "I need to schedule a team meeting for next week"
        ]
        
        for example in example_messages:
            if st.button(f"💬 {example}", key=f"example_{hash(example)}"):
                st.session_state.example_message = example
        
        st.markdown("---")
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
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
        
        # Get response from mock backend
        with st.spinner("🤔 Thinking..."):
            response_data = st.session_state.mock_backend.process_chat(user_input, st.session_state.session_id)
        
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
        AI Calendar Booking Agent | Built with FastAPI, LangGraph & Streamlit<br>
        <a href="https://github.com/Anant-Joshi123/chatbot" target="_blank">🔗 View Source Code on GitHub</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
