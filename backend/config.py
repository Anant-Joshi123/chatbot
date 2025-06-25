"""
Configuration settings for the booking agent.
"""

import os
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Calendar
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_CALENDAR_TOKEN_FILE: str = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")
    DEFAULT_CALENDAR_ID: str = os.getenv("DEFAULT_CALENDAR_ID", "primary")
    
    # Server Settings
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "localhost")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", 8000))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))
    
    # Calendar Settings
    TIMEZONE: str = os.getenv("TIMEZONE", "America/New_York")
    DEFAULT_MEETING_DURATION: int = 60  # minutes
    WORKING_HOURS: Tuple[int, int] = (9, 17)  # 9 AM to 5 PM
    MAX_AVAILABILITY_DAYS: int = 30  # Look ahead 30 days max
    MAX_AVAILABLE_SLOTS: int = 10  # Return max 10 available slots
    
    # Agent Settings
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.1
    MAX_CONVERSATION_HISTORY: int = 20  # Keep last 20 messages
    
    # Session Settings
    SESSION_TIMEOUT_HOURS: int = 24  # Sessions expire after 24 hours
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings."""
        required_settings = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing = []
        for name, value in required_settings:
            if not value:
                missing.append(name)
        
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            return False
        
        return True


settings = Settings()
