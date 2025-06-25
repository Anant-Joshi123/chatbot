"""
FastAPI backend for the AI Calendar Booking Agent.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from backend.models.schemas import (
    ChatMessage, ChatResponse, BookingRequest, BookingResponse,
    AvailabilityRequest, AvailabilityResponse
)

# Try to import the full agent, fall back to simple agent
try:
    from backend.agent.booking_agent import BookingAgent
    FULL_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Full agent not available: {e}")
    FULL_AGENT_AVAILABLE = False

from backend.agent.simple_agent import SimpleBookingAgent

# Try to import Google Calendar, fall back to mock
try:
    from backend.calendar.google_calendar import GoogleCalendarService
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Google Calendar not available: {e}")
    GOOGLE_CALENDAR_AVAILABLE = False

from backend.calendar.mock_calendar import MockCalendarService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Calendar Booking Agent",
    description="A conversational AI agent for booking calendar appointments",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
booking_agent = None
calendar_service = None

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global booking_agent, calendar_service

    try:
        # Initialize calendar service
        if GOOGLE_CALENDAR_AVAILABLE and os.path.exists('credentials.json'):
            try:
                calendar_service = GoogleCalendarService()
                print("✅ Google Calendar service initialized")
            except Exception as e:
                print(f"⚠️  Google Calendar failed, using mock: {e}")
                calendar_service = MockCalendarService()
        else:
            calendar_service = MockCalendarService()
            print("✅ Mock calendar service initialized")

        # Initialize booking agent
        openai_key = os.getenv("OPENAI_API_KEY")
        if FULL_AGENT_AVAILABLE and openai_key and openai_key != "your_openai_api_key_here":
            try:
                booking_agent = BookingAgent()
                print("✅ Full AI agent initialized")
            except Exception as e:
                print(f"⚠️  Full agent failed, using simple agent: {e}")
                booking_agent = SimpleBookingAgent()
        else:
            booking_agent = SimpleBookingAgent()
            print("✅ Simple rule-based agent initialized")
            if not openai_key or openai_key == "your_openai_api_key_here":
                print("💡 Add your OpenAI API key to .env for full AI capabilities")

        print("🚀 Backend services ready!")

    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        # Initialize with fallback services
        booking_agent = SimpleBookingAgent()
        calendar_service = MockCalendarService()
        print("🔄 Fallback services initialized")


def get_booking_agent():
    """Dependency to get booking agent instance."""
    if booking_agent is None:
        raise HTTPException(status_code=503, detail="Booking agent not initialized")
    return booking_agent


def get_calendar_service():
    """Dependency to get calendar service instance."""
    if calendar_service is None:
        raise HTTPException(status_code=503, detail="Calendar service not initialized")
    return calendar_service


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Calendar Booking Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "booking_agent": booking_agent is not None,
            "calendar_service": calendar_service is not None
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    agent: BookingAgent = Depends(get_booking_agent)
):
    """
    Main chat endpoint for conversing with the booking agent.
    """
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Initialize session if new
        if session_id not in sessions:
            sessions[session_id] = {
                "created_at": datetime.utcnow(),
                "messages": [],
                "state": "active"
            }
        
        # Add user message to session
        sessions[session_id]["messages"].append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Process message with agent
        result = agent.process_message(message.message, session_id)
        
        # Add agent response to session
        sessions[session_id]["messages"].append({
            "role": "assistant",
            "content": result["response"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            intent=result.get("intent"),
            extracted_info=result.get("extracted_info"),
            available_slots=result.get("available_slots"),
            booking_confirmed=result.get("booking_confirmed", False)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/book", response_model=BookingResponse)
async def book_appointment(
    booking: BookingRequest,
    calendar: GoogleCalendarService = Depends(get_calendar_service)
):
    """
    Direct booking endpoint for creating calendar events.
    """
    try:
        event_id = calendar.create_event(
            title=booking.title,
            start_time=booking.start_time,
            end_time=booking.end_time,
            description=booking.description,
            attendee_email=booking.attendee_email
        )
        
        if event_id:
            return BookingResponse(
                success=True,
                event_id=event_id,
                message="Appointment booked successfully!"
            )
        else:
            return BookingResponse(
                success=False,
                message="Failed to create calendar event"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error booking appointment: {str(e)}")


@app.post("/availability", response_model=AvailabilityResponse)
async def check_availability(
    request: AvailabilityRequest,
    calendar: GoogleCalendarService = Depends(get_calendar_service)
):
    """
    Check calendar availability for a given date range.
    """
    try:
        available_slots = calendar.find_available_slots(
            start_date=request.start_date,
            end_date=request.end_date,
            duration_minutes=request.duration_minutes
        )
        
        return AvailabilityResponse(
            available_slots=available_slots,
            message=f"Found {len(available_slots)} available slots"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get session information and conversation history.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and its conversation history.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": "Session deleted successfully"}


@app.get("/sessions")
async def list_sessions():
    """
    List all active sessions.
    """
    return {
        "sessions": list(sessions.keys()),
        "total": len(sessions)
    }


@app.get("/events")
async def get_upcoming_events(
    max_results: int = 10,
    calendar: GoogleCalendarService = Depends(get_calendar_service)
):
    """
    Get upcoming calendar events.
    """
    try:
        events = calendar.get_upcoming_events(max_results=max_results)
        return {
            "events": events,
            "total": len(events)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
