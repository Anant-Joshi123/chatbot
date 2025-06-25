"""
LangGraph-based booking agent for calendar appointments.
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.models.schemas import AgentState
from backend.calendar.google_calendar import GoogleCalendarService


class BookingAgent:
    """Conversational booking agent using LangGraph."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.calendar_service = GoogleCalendarService()
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph conversation flow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("extract_info", self._extract_info)
        workflow.add_node("check_availability", self._check_availability)
        workflow.add_node("confirm_booking", self._confirm_booking)
        workflow.add_node("create_event", self._create_event)
        workflow.add_node("generate_response", self._generate_response)
        
        # Set entry point
        workflow.set_entry_point("analyze_intent")
        
        # Add edges
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_after_intent,
            {
                "extract_info": "extract_info",
                "check_availability": "check_availability",
                "confirm_booking": "confirm_booking",
                "generate_response": "generate_response"
            }
        )
        
        workflow.add_edge("extract_info", "check_availability")
        workflow.add_edge("check_availability", "generate_response")
        workflow.add_edge("confirm_booking", "create_event")
        workflow.add_edge("create_event", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _analyze_intent(self, state: AgentState) -> AgentState:
        """Analyze user intent from the message."""
        last_message = state.messages[-1]["content"] if state.messages else ""
        
        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for a calendar booking agent. 
            Analyze the user's message and classify the intent into one of these categories:
            - greeting: General greeting or introduction
            - book_meeting: User wants to schedule a meeting/appointment
            - check_availability: User wants to see available times
            - confirm_booking: User is confirming a specific time slot
            - modify_booking: User wants to change booking details
            - cancel_booking: User wants to cancel a booking
            - other: Other intents
            
            Current conversation step: {current_step}
            
            Respond with just the intent category."""),
            ("human", "{message}")
        ])
        
        response = self.llm.invoke(
            intent_prompt.format_messages(
                message=last_message,
                current_step=state.current_step
            )
        )
        
        state.intent = response.content.strip().lower()
        return state
    
    def _extract_info(self, state: AgentState) -> AgentState:
        """Extract booking information from user messages."""
        messages_text = "\n".join([msg["content"] for msg in state.messages if msg["role"] == "user"])
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an information extraction agent for calendar booking.
            Extract the following information from the user's messages:
            - date: Any mentioned dates (convert to YYYY-MM-DD format)
            - time: Any mentioned times (convert to HH:MM format)
            - duration: Meeting duration in minutes (default 60 if not specified)
            - title: Meeting title or purpose
            - description: Additional details about the meeting
            - attendee_email: Any email addresses mentioned
            
            Current date: {current_date}
            Current time: {current_time}
            
            Handle relative dates like "tomorrow", "next week", "Friday", etc.
            
            Return the information as a JSON object. Use null for missing information."""),
            ("human", "{messages}")
        ])
        
        now = datetime.now(self.timezone)
        response = self.llm.invoke(
            extraction_prompt.format_messages(
                messages=messages_text,
                current_date=now.strftime("%Y-%m-%d"),
                current_time=now.strftime("%H:%M")
            )
        )
        
        try:
            extracted = json.loads(response.content)
            state.extracted_info.update(extracted)
        except json.JSONDecodeError:
            # Fallback to simple regex extraction
            state.extracted_info.update(self._simple_extract(messages_text))
        
        return state
    
    def _simple_extract(self, text: str) -> Dict[str, Any]:
        """Simple regex-based information extraction as fallback."""
        info = {}
        
        # Extract dates
        date_patterns = [
            r'tomorrow',
            r'today',
            r'next week',
            r'this week',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text.lower())
            if match:
                info['date'] = match.group()
                break
        
        # Extract times
        time_pattern = r'\d{1,2}:\d{2}\s*(am|pm)?|\d{1,2}\s*(am|pm)'
        time_match = re.search(time_pattern, text.lower())
        if time_match:
            info['time'] = time_match.group()
        
        # Extract duration
        duration_pattern = r'(\d+)\s*(hour|hr|minute|min)'
        duration_match = re.search(duration_pattern, text.lower())
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            if 'hour' in unit or 'hr' in unit:
                info['duration'] = value * 60
            else:
                info['duration'] = value
        
        return info
    
    def _check_availability(self, state: AgentState) -> AgentState:
        """Check calendar availability based on extracted information."""
        extracted = state.extracted_info
        
        # Determine date range
        start_date = self._parse_date(extracted.get('date'))
        if not start_date:
            start_date = datetime.now(self.timezone) + timedelta(days=1)  # Default to tomorrow
        
        end_date = start_date + timedelta(days=7)  # Check next 7 days
        
        # Get duration
        duration = extracted.get('duration', 60)
        
        # Find available slots
        available_slots = self.calendar_service.find_available_slots(
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration
        )
        
        state.available_slots = available_slots
        return state
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        now = datetime.now(self.timezone)
        date_str = date_str.lower().strip()
        
        if date_str == 'today':
            return now
        elif date_str == 'tomorrow':
            return now + timedelta(days=1)
        elif date_str == 'next week':
            return now + timedelta(days=7)
        elif date_str in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            # Find next occurrence of this weekday
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_weekday = weekdays.index(date_str)
            days_ahead = target_weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return now + timedelta(days=days_ahead)
        
        # Try to parse other formats
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
        
        try:
            return datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            pass
        
        return None
    
    def _confirm_booking(self, state: AgentState) -> AgentState:
        """Handle booking confirmation."""
        last_message = state.messages[-1]["content"].lower()
        
        # Check if user is confirming
        confirmation_words = ['yes', 'confirm', 'book', 'schedule', 'ok', 'sure', 'sounds good']
        is_confirming = any(word in last_message for word in confirmation_words)
        
        if is_confirming and state.available_slots:
            # For simplicity, book the first available slot
            # In a real implementation, you'd let user choose
            state.selected_slot = state.available_slots[0]
            state.booking_confirmed = True
        
        return state
    
    def _create_event(self, state: AgentState) -> AgentState:
        """Create the calendar event."""
        if not state.selected_slot:
            return state
        
        slot = state.selected_slot
        title = state.extracted_info.get('title', 'Meeting')
        description = state.extracted_info.get('description', 'Scheduled via AI booking agent')
        attendee_email = state.extracted_info.get('attendee_email')
        
        event_id = self.calendar_service.create_event(
            title=title,
            start_time=slot['start'],
            end_time=slot['end'],
            description=description,
            attendee_email=attendee_email
        )
        
        if event_id:
            state.current_step = "completed"
            state.extracted_info['event_id'] = event_id
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate appropriate response based on current state."""
        # Determine response based on current state and intent
        if state.intent == "greeting":
            state.final_response = self._generate_greeting_response()
        elif state.intent in ["book_meeting", "check_availability"]:
            state.final_response = self._generate_booking_response(state)
        elif state.intent == "confirm_booking":
            state.final_response = self._generate_confirmation_response(state)
        elif state.booking_confirmed and state.extracted_info.get('event_id'):
            state.final_response = self._generate_success_response(state)
        else:
            state.final_response = self._generate_general_response(state)

        return state

    def _generate_greeting_response(self) -> str:
        """Generate a greeting response."""
        greetings = [
            "Hello! I'm your AI calendar assistant. I can help you schedule meetings and check your availability. What would you like to do today?",
            "Hi there! I'm here to help you book appointments and manage your calendar. How can I assist you?",
            "Welcome! I can help you find available time slots and schedule meetings. What do you need help with?"
        ]
        return greetings[0]  # For consistency, use the first one

    def _generate_booking_response(self, state: AgentState) -> str:
        """Generate response for booking-related intents."""
        extracted = state.extracted_info

        if not state.available_slots:
            # Need more information or no slots found
            missing_info = []
            if not extracted.get('date'):
                missing_info.append("preferred date")
            if not extracted.get('time') and not extracted.get('date'):
                missing_info.append("preferred time")

            if missing_info:
                return f"I'd be happy to help you schedule a meeting! Could you please provide your {' and '.join(missing_info)}? For example, you could say 'tomorrow at 2 PM' or 'next Friday afternoon'."
            else:
                return "I couldn't find any available slots for your requested time. Let me check some alternative times for you."

        # Show available slots
        response = "Great! I found some available time slots for you:\n\n"
        for i, slot in enumerate(state.available_slots[:3], 1):
            response += f"{i}. {slot['date']} from {slot['start_time']} to {slot['end_time']}\n"

        response += "\nWhich time works best for you? Just let me know the number or tell me your preference!"
        return response

    def _generate_confirmation_response(self, state: AgentState) -> str:
        """Generate response for booking confirmation."""
        if state.booking_confirmed:
            return "Perfect! I'm booking that time slot for you now..."
        else:
            return "I'd be happy to help you choose a time slot. Could you please specify which option you prefer, or let me know if you'd like to see different times?"

    def _generate_success_response(self, state: AgentState) -> str:
        """Generate response for successful booking."""
        slot = state.selected_slot
        event_id = state.extracted_info.get('event_id')

        if slot and event_id:
            return f"""✅ **Booking Confirmed!**

Your meeting has been successfully scheduled for:
📅 **Date:** {slot['date']}
🕐 **Time:** {slot['start_time']} - {slot['end_time']}
📝 **Event ID:** {event_id[:8]}...

You should receive a calendar invitation shortly. Is there anything else I can help you with?"""
        else:
            return "Your booking has been confirmed! You should receive a calendar invitation shortly."

    def _generate_general_response(self, state: AgentState) -> str:
        """Generate a general response using LLM."""
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful calendar booking assistant. Respond naturally and helpfully to the user's message.

            Context:
            - Current step: {current_step}
            - Intent: {intent}
            - Available information: {extracted_info}

            Guidelines:
            - Be conversational and friendly
            - If the user seems confused, offer to help with booking
            - If they ask about something unrelated to calendar booking, politely redirect
            - Keep responses concise but helpful"""),
            ("human", "{last_message}")
        ])

        last_message = state.messages[-1]["content"] if state.messages else ""

        response = self.llm.invoke(
            response_prompt.format_messages(
                current_step=state.current_step,
                intent=state.intent or "unknown",
                extracted_info=json.dumps(state.extracted_info),
                last_message=last_message
            )
        )

        return response.content
    
    def _route_after_intent(self, state: AgentState) -> str:
        """Route to next node based on intent."""
        intent = state.intent
        
        if intent in ['book_meeting', 'check_availability']:
            return "extract_info"
        elif intent == 'confirm_booking':
            return "confirm_booking"
        else:
            return "generate_response"
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process a user message and return response."""
        # Create initial state
        initial_state = AgentState(
            messages=[{"role": "user", "content": message}],
            session_id=session_id
        )
        
        # Run the graph
        config = {"configurable": {"thread_id": session_id}}
        result = self.graph.invoke(initial_state, config)
        
        return {
            "response": result.final_response,
            "session_id": session_id,
            "intent": result.intent,
            "extracted_info": result.extracted_info,
            "available_slots": result.available_slots,
            "booking_confirmed": result.booking_confirmed
        }
