"""
Pydantic models for the booking agent API.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    intent: Optional[str] = Field(None, description="Detected intent")
    extracted_info: Optional[Dict[str, Any]] = Field(None, description="Extracted booking information")
    available_slots: Optional[List[Dict]] = Field(None, description="Available time slots")
    booking_confirmed: bool = Field(False, description="Whether booking was confirmed")


class BookingRequest(BaseModel):
    """Booking request model."""
    title: str = Field(..., description="Meeting title")
    start_time: datetime = Field(..., description="Meeting start time")
    end_time: datetime = Field(..., description="Meeting end time")
    description: Optional[str] = Field("", description="Meeting description")
    attendee_email: Optional[str] = Field(None, description="Attendee email")


class BookingResponse(BaseModel):
    """Booking response model."""
    success: bool = Field(..., description="Whether booking was successful")
    event_id: Optional[str] = Field(None, description="Created event ID")
    message: str = Field(..., description="Response message")


class AvailabilityRequest(BaseModel):
    """Availability request model."""
    start_date: datetime = Field(..., description="Start date for availability check")
    end_date: datetime = Field(..., description="End date for availability check")
    duration_minutes: int = Field(60, description="Meeting duration in minutes")


class AvailabilityResponse(BaseModel):
    """Availability response model."""
    available_slots: List[Dict] = Field(..., description="List of available time slots")
    message: str = Field(..., description="Response message")


class ConversationState(BaseModel):
    """Conversation state model for tracking booking progress."""
    session_id: str
    intent: Optional[str] = None
    extracted_info: Dict[str, Any] = Field(default_factory=dict)
    current_step: str = "greeting"  # greeting, collecting_info, showing_availability, confirming, completed
    available_slots: List[Dict] = Field(default_factory=list)
    selected_slot: Optional[Dict] = None
    booking_details: Optional[Dict] = None
    conversation_history: List[Dict] = Field(default_factory=list)


class AgentState(BaseModel):
    """State model for LangGraph agent."""
    messages: List[Dict] = Field(default_factory=list)
    session_id: str
    intent: Optional[str] = None
    extracted_info: Dict[str, Any] = Field(default_factory=dict)
    current_step: str = "greeting"
    available_slots: List[Dict] = Field(default_factory=list)
    selected_slot: Optional[Dict] = None
    booking_confirmed: bool = False
    final_response: Optional[str] = None
