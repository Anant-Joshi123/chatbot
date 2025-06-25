"""
Google Calendar integration for the booking agent.
Handles authentication, availability checking, and event creation.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """Service class for Google Calendar operations."""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file {self.credentials_file} not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_free_busy(self, start_time: datetime, end_time: datetime, 
                      calendar_id: str = 'primary') -> List[Dict]:
        """
        Get free/busy information for a time range.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range
            calendar_id: Calendar ID to check
            
        Returns:
            List of busy time slots
        """
        try:
            body = {
                "timeMin": start_time.isoformat(),
                "timeMax": end_time.isoformat(),
                "timeZone": str(self.timezone),
                "items": [{"id": calendar_id}]
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            busy_times = freebusy_result['calendars'][calendar_id].get('busy', [])
            
            return busy_times
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def find_available_slots(self, start_date: datetime, end_date: datetime,
                           duration_minutes: int = 60, 
                           working_hours: Tuple[int, int] = (9, 17),
                           calendar_id: str = 'primary') -> List[Dict]:
        """
        Find available time slots within a date range.
        
        Args:
            start_date: Start date to search
            end_date: End date to search
            duration_minutes: Duration of the meeting in minutes
            working_hours: Tuple of (start_hour, end_hour) in 24-hour format
            calendar_id: Calendar ID to check
            
        Returns:
            List of available time slots
        """
        available_slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Create datetime objects for the working day
            day_start = self.timezone.localize(
                datetime.combine(current_date, datetime.min.time().replace(hour=working_hours[0]))
            )
            day_end = self.timezone.localize(
                datetime.combine(current_date, datetime.min.time().replace(hour=working_hours[1]))
            )
            
            # Get busy times for this day
            busy_times = self.get_free_busy(day_start, day_end, calendar_id)
            
            # Convert busy times to datetime objects
            busy_periods = []
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                busy_periods.append((busy_start, busy_end))
            
            # Sort busy periods by start time
            busy_periods.sort(key=lambda x: x[0])
            
            # Find free slots
            current_time = day_start
            for busy_start, busy_end in busy_periods:
                # Check if there's a free slot before this busy period
                if current_time + timedelta(minutes=duration_minutes) <= busy_start:
                    available_slots.append({
                        'start': current_time,
                        'end': current_time + timedelta(minutes=duration_minutes),
                        'date': current_date.strftime('%Y-%m-%d'),
                        'start_time': current_time.strftime('%I:%M %p'),
                        'end_time': (current_time + timedelta(minutes=duration_minutes)).strftime('%I:%M %p')
                    })
                
                current_time = max(current_time, busy_end)
            
            # Check for free slot after the last busy period
            if current_time + timedelta(minutes=duration_minutes) <= day_end:
                available_slots.append({
                    'start': current_time,
                    'end': current_time + timedelta(minutes=duration_minutes),
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': current_time.strftime('%I:%M %p'),
                    'end_time': (current_time + timedelta(minutes=duration_minutes)).strftime('%I:%M %p')
                })
            
            current_date += timedelta(days=1)
        
        return available_slots[:10]  # Return max 10 slots
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime,
                     description: str = "", attendee_email: str = None,
                     calendar_id: str = 'primary') -> Optional[str]:
        """
        Create a calendar event.
        
        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            attendee_email: Email of attendee to invite
            calendar_id: Calendar ID to create event in
            
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return event.get('id')
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_upcoming_events(self, max_results: int = 10, 
                          calendar_id: str = 'primary') -> List[Dict]:
        """
        Get upcoming events from the calendar.
        
        Args:
            max_results: Maximum number of events to return
            calendar_id: Calendar ID to query
            
        Returns:
            List of upcoming events
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            
            events_result = self.service.events().list(
                calendarId=calendar_id, timeMin=now,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime').execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'description': event.get('description', '')
                })
            
            return formatted_events
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
