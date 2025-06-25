"""
Simple booking agent that works without OpenAI API for testing.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz

from backend.calendar.mock_calendar import MockCalendarService


class SimpleBookingAgent:
    """Simple rule-based booking agent for testing without OpenAI API."""
    
    def __init__(self):
        self.calendar_service = MockCalendarService()
        self.timezone = pytz.timezone('America/New_York')
        self.sessions = {}
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process a user message and return response."""
        
        # Initialize session if new
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'step': 'greeting',
                'extracted_info': {},
                'available_slots': [],
                'selected_slot': None
            }
        
        session = self.sessions[session_id]
        message_lower = message.lower().strip()
        
        # Analyze intent
        intent = self._analyze_intent(message_lower)

        # Extract information
        extracted_info = self._extract_info(message)
        session['extracted_info'].update(extracted_info)

        print(f"DEBUG: Session step: {session['step']}, Intent: {intent}, Extracted: {extracted_info}")
        
        # Generate response based on intent and session state
        if intent == 'greeting' and session['step'] == 'greeting':
            response = self._handle_greeting()
            session['step'] = 'collecting_info'

        elif intent in ['book_meeting', 'check_availability']:
            response = self._handle_booking_request(session)
            if session.get('available_slots'):
                session['step'] = 'showing_slots'
            else:
                session['step'] = 'collecting_info'

        elif session['step'] == 'collecting_info':
            # Continue collecting information
            response = self._handle_booking_request(session)
            if session.get('available_slots'):
                session['step'] = 'showing_slots'

        elif intent == 'select_slot' or session['step'] == 'showing_slots':
            response = self._handle_slot_selection(session, message)
            if session.get('selected_slot'):
                session['step'] = 'confirming'

        elif intent == 'confirm_booking' or session['step'] == 'confirming':
            response = self._handle_confirmation(session, message_lower)

        else:
            response = self._handle_general(message)

        print(f"DEBUG: After processing - Session step: {session['step']}, Response: {response[:50]}...")
        
        return {
            "response": response,
            "session_id": session_id,
            "intent": intent,
            "extracted_info": session['extracted_info'],
            "available_slots": session.get('available_slots', []),
            "booking_confirmed": session.get('booking_confirmed', False)
        }
    
    def _analyze_intent(self, message: str) -> str:
        """Simple rule-based intent analysis."""
        
        greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        booking_words = ['schedule', 'book', 'meeting', 'appointment', 'call', 'time']
        availability_words = ['available', 'free', 'open', 'when']
        confirmation_words = ['yes', 'confirm', 'ok', 'sure', 'sounds good', 'perfect']
        selection_words = ['first', 'second', 'third', 'option', '1', '2', '3']
        
        if any(word in message for word in greeting_words) and len(message.split()) <= 3:
            return 'greeting'
        elif any(word in message for word in confirmation_words):
            return 'confirm_booking'
        elif any(word in message for word in selection_words):
            return 'select_slot'
        elif any(word in message for word in booking_words) or any(word in message for word in availability_words):
            return 'book_meeting'
        else:
            return 'general'
    
    def _extract_info(self, message: str) -> Dict[str, Any]:
        """Extract booking information from message."""
        info = {}
        message_lower = message.lower()
        
        # Extract dates
        if 'tomorrow' in message_lower:
            tomorrow = datetime.now(self.timezone) + timedelta(days=1)
            info['date'] = tomorrow.strftime('%Y-%m-%d')
        elif 'today' in message_lower:
            today = datetime.now(self.timezone)
            info['date'] = today.strftime('%Y-%m-%d')
        elif 'next week' in message_lower:
            next_week = datetime.now(self.timezone) + timedelta(days=7)
            info['date'] = next_week.strftime('%Y-%m-%d')
        elif 'friday' in message_lower:
            # Find next Friday
            today = datetime.now(self.timezone)
            days_ahead = 4 - today.weekday()  # Friday is 4
            if days_ahead <= 0:
                days_ahead += 7
            friday = today + timedelta(days=days_ahead)
            info['date'] = friday.strftime('%Y-%m-%d')
        elif 'monday' in message_lower:
            # Find next Monday
            today = datetime.now(self.timezone)
            days_ahead = 0 - today.weekday()  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            monday = today + timedelta(days=days_ahead)
            info['date'] = monday.strftime('%Y-%m-%d')
        
        # Extract times
        time_patterns = [
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'afternoon',
            r'morning',
            r'evening'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info['time'] = match.group()
                break
        
        # Extract duration
        if '30' in message and 'minute' in message_lower:
            info['duration'] = 30
        elif '1 hour' in message_lower or 'one hour' in message_lower:
            info['duration'] = 60
        elif '2 hour' in message_lower or 'two hour' in message_lower:
            info['duration'] = 120
        
        # Extract meeting type/title
        if 'team' in message_lower:
            info['title'] = 'Team Meeting'
        elif 'client' in message_lower:
            info['title'] = 'Client Meeting'
        elif 'call' in message_lower:
            info['title'] = 'Phone Call'
        elif 'consultation' in message_lower:
            info['title'] = 'Consultation'
        
        return info
    
    def _handle_greeting(self) -> str:
        """Handle greeting messages."""
        return "Hello! I'm your AI calendar assistant. I can help you schedule meetings and check your availability. What would you like to do today?"
    
    def _handle_booking_request(self, session: Dict) -> str:
        """Handle booking requests."""
        extracted = session['extracted_info']

        # Check if we already have slots and are just continuing the conversation
        if session.get('available_slots') and session['step'] == 'showing_slots':
            # Show available slots again
            available_slots = session['available_slots']
            response = "Here are the available time slots again:\n\n"
            for i, slot in enumerate(available_slots[:3], 1):
                response += f"{i}. {slot['date']} from {slot['start_time']} to {slot['end_time']}\n"
            response += "\nWhich option works best for you? You can say 'option 1', 'the first one', or just '1'."
            return response

        # Check if we have enough information
        if not extracted.get('date'):
            return "I'd be happy to help you schedule a meeting! Could you please tell me your preferred date? For example, you could say 'tomorrow', 'next Friday', or a specific date."

        # Get available slots
        start_date = self._parse_date(extracted.get('date'))
        if not start_date:
            start_date = datetime.now(self.timezone) + timedelta(days=1)

        end_date = start_date + timedelta(days=7)
        duration = extracted.get('duration', 60)

        available_slots = self.calendar_service.find_available_slots(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration
        )

        session['available_slots'] = available_slots

        if not available_slots:
            return "I couldn't find any available slots for your requested time. Could you try a different date or time range?"

        # Show available slots
        response = "Great! I found some available time slots for you:\n\n"
        for i, slot in enumerate(available_slots[:3], 1):
            response += f"{i}. {slot['date']} from {slot['start_time']} to {slot['end_time']}\n"

        response += "\nWhich option works best for you? You can say 'option 1', 'the first one', or just '1'."
        return response
    
    def _handle_slot_selection(self, session: Dict, message: str) -> str:
        """Handle slot selection."""
        available_slots = session.get('available_slots', [])
        if not available_slots:
            return "I don't see any available slots to choose from. Let me help you find some times first."

        # Parse selection
        message_lower = message.lower()
        selected_index = None

        # More flexible selection parsing
        if 'first' in message_lower or '1' in message or 'option 1' in message_lower:
            selected_index = 0
        elif 'second' in message_lower or '2' in message or 'option 2' in message_lower:
            selected_index = 1
        elif 'third' in message_lower or '3' in message or 'option 3' in message_lower:
            selected_index = 2
        elif 'looks good' in message_lower or 'good' in message_lower or 'that one' in message_lower:
            # Default to first option if they say it looks good
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
                # Create the event
                title = session['extracted_info'].get('title', 'Meeting')
                event_id = self.calendar_service.create_event(
                    title=title,
                    start_time=selected_slot['start'],
                    end_time=selected_slot['end'],
                    description='Scheduled via AI booking agent'
                )
                
                session['booking_confirmed'] = True
                
                return f"""✅ **Booking Confirmed!**

Your meeting has been successfully scheduled:
📅 **Date:** {selected_slot['date']}
🕐 **Time:** {selected_slot['start_time']} - {selected_slot['end_time']}
📝 **Title:** {title}
🆔 **Event ID:** {event_id[:8]}...

Is there anything else I can help you with?"""
            else:
                return "I don't see a selected time slot to confirm. Please choose a time slot first."
        else:
            return "No problem! Would you like to see different time options or make changes to your booking request?"
    
    def _handle_general(self, message: str) -> str:
        """Handle general messages."""
        return "I'm here to help you schedule meetings and manage your calendar. You can ask me to 'schedule a meeting', 'check availability', or 'book an appointment'. How can I assist you today?"
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
