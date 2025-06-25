"""
Mock calendar service for testing without Google Calendar API.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz
import random
import uuid


class MockCalendarService:
    """Mock calendar service that simulates Google Calendar functionality."""
    
    def __init__(self):
        self.timezone = pytz.timezone('America/New_York')
        self.events = []  # Store mock events
    
    def get_free_busy(self, start_time: datetime, end_time: datetime, 
                      calendar_id: str = 'primary') -> List[Dict]:
        """
        Mock free/busy information - returns some random busy times.
        """
        busy_times = []
        
        # Add some mock busy periods
        current = start_time
        while current < end_time:
            # 30% chance of having a busy period
            if random.random() < 0.3:
                busy_start = current
                busy_end = current + timedelta(hours=1)
                if busy_end <= end_time:
                    busy_times.append({
                        'start': busy_start.isoformat(),
                        'end': busy_end.isoformat()
                    })
            current += timedelta(hours=2)
        
        return busy_times
    
    def find_available_slots(self, start_date: datetime, end_date: datetime,
                           duration_minutes: int = 60, 
                           working_hours: Tuple[int, int] = (9, 17),
                           calendar_id: str = 'primary') -> List[Dict]:
        """
        Find available time slots within a date range.
        """
        available_slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        slot_count = 0
        max_slots = 10
        
        while current_date <= end_date_only and slot_count < max_slots:
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Generate some available slots for each day
            for hour in range(working_hours[0], working_hours[1], 2):
                if slot_count >= max_slots:
                    break
                
                # 70% chance of slot being available
                if random.random() < 0.7:
                    slot_start = self.timezone.localize(
                        datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                    )
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    available_slots.append({
                        'start': slot_start,
                        'end': slot_end,
                        'date': current_date.strftime('%Y-%m-%d'),
                        'start_time': slot_start.strftime('%I:%M %p'),
                        'end_time': slot_end.strftime('%I:%M %p')
                    })
                    slot_count += 1
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime,
                     description: str = "", attendee_email: str = None,
                     calendar_id: str = 'primary') -> Optional[str]:
        """
        Create a mock calendar event.
        """
        event_id = str(uuid.uuid4())
        
        event = {
            'id': event_id,
            'title': title,
            'start_time': start_time,
            'end_time': end_time,
            'description': description,
            'attendee_email': attendee_email,
            'created_at': datetime.now()
        }
        
        self.events.append(event)
        print(f"📅 Mock event created: {title} on {start_time.strftime('%Y-%m-%d %H:%M')}")
        
        return event_id
    
    def get_upcoming_events(self, max_results: int = 10, 
                          calendar_id: str = 'primary') -> List[Dict]:
        """
        Get upcoming mock events.
        """
        now = datetime.now(self.timezone)
        upcoming_events = []
        
        # Add some mock upcoming events
        for i in range(min(3, max_results)):
            event_time = now + timedelta(days=i+1, hours=10+i*2)
            upcoming_events.append({
                'id': f'mock_event_{i}',
                'summary': f'Mock Meeting {i+1}',
                'start': event_time.isoformat(),
                'description': f'This is a mock event for testing purposes'
            })
        
        # Add any created events
        for event in self.events:
            if event['start_time'] > now:
                upcoming_events.append({
                    'id': event['id'],
                    'summary': event['title'],
                    'start': event['start_time'].isoformat(),
                    'description': event['description']
                })
        
        return upcoming_events[:max_results]
