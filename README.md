# AI Calendar Booking Agent

A conversational AI agent that assists users in booking appointments on Google Calendar using natural language interactions.

## Features

- 🤖 Natural language conversation for appointment booking
- 📅 Google Calendar integration for availability checking and booking
- 💬 Streamlit chat interface for seamless user experience
- 🚀 FastAPI backend with LangGraph agent framework
- 🔄 Real-time calendar availability checking
- ✅ Intelligent conversation flow handling

## Tech Stack

- **Backend**: Python with FastAPI
- **Agent Framework**: LangGraph
- **Frontend**: Streamlit
- **Calendar Integration**: Google Calendar API
- **AI**: OpenAI GPT models via LangChain

## Quick Start

### Option 1: Automated Setup
```bash
# Run the setup script
python setup.py

# Edit .env file with your API keys
# Add your OpenAI API key and Google Calendar credentials

# Start the backend
python run_backend.py

# In another terminal, start the frontend
python run_frontend.py
```

### Option 2: Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. **Set up Google Calendar API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to project root

4. **Add your OpenAI API Key**
   ```bash
   # In .env file
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**
   ```bash
   # Terminal 1: Start backend
   python run_backend.py

   # Terminal 2: Start frontend
   python run_frontend.py
   ```

## Usage

1. **Access the Application**
   - Frontend UI: `http://localhost:8501`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

2. **Start Chatting**
   - Open the Streamlit interface
   - Type your message in the chat input
   - The AI agent will respond and guide you through booking

3. **Booking Process**
   - Express your intent to book a meeting
   - Provide date/time preferences when asked
   - Review available time slots
   - Confirm your preferred slot
   - Receive booking confirmation

## Example Conversations

### Basic Booking
```
User: "Hi, I'd like to schedule a meeting"
Agent: "Hello! I'd be happy to help you schedule a meeting. Could you please provide your preferred date and time?"

User: "Tomorrow at 2 PM"
Agent: "Great! I found some available time slots for you:
1. 2024-12-27 from 02:00 PM to 03:00 PM
2. 2024-12-27 from 02:30 PM to 03:30 PM
Which time works best for you?"

User: "The first option looks good"
Agent: "Perfect! I'm booking that time slot for you now..."
```

### Natural Language Requests
- "Hey, I want to schedule a call for tomorrow afternoon."
- "Do you have any free time this Friday?"
- "Book a meeting between 3-5 PM next week."
- "I need a 30-minute slot sometime next Monday."
- "Can we meet for an hour this Thursday morning?"

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── agent/
│   │   ├── __init__.py
│   │   └── booking_agent.py # LangGraph agent implementation
│   ├── calendar/
│   │   ├── __init__.py
│   │   └── google_calendar.py # Google Calendar integration
│   └── models/
│       ├── __init__.py
│       └── schemas.py       # Pydantic models
├── frontend/
│   └── app.py               # Streamlit chat interface
├── run_backend.py           # Backend startup script
├── run_frontend.py          # Frontend startup script
├── setup.py                 # Automated setup script
├── test_agent.py            # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Features

### 🤖 Conversational AI
- Natural language understanding for booking requests
- Context-aware conversation flow
- Intent recognition and information extraction
- Multi-turn conversation handling

### 📅 Calendar Integration
- Real-time Google Calendar availability checking
- Automatic event creation with details
- Conflict detection and resolution
- Timezone handling

### 💬 User Interface
- Clean, intuitive Streamlit chat interface
- Real-time message exchange
- Visual availability slot display
- Session management and history

### 🔧 Technical Features
- FastAPI backend with automatic API documentation
- LangGraph for sophisticated conversation flows
- Pydantic models for data validation
- Comprehensive error handling and logging
- Modular, extensible architecture

## API Endpoints

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "I want to schedule a meeting",
  "session_id": "optional-session-id"
}
```

### Direct Booking
```http
POST /book
Content-Type: application/json

{
  "title": "Team Meeting",
  "start_time": "2024-12-27T14:00:00",
  "end_time": "2024-12-27T15:00:00",
  "description": "Weekly team sync",
  "attendee_email": "colleague@example.com"
}
```

### Check Availability
```http
POST /availability
Content-Type: application/json

{
  "start_date": "2024-12-27T00:00:00",
  "end_date": "2024-12-30T23:59:59",
  "duration_minutes": 60
}
```

## Testing

Run the comprehensive test suite:

```bash
# Make sure the backend is running first
python run_backend.py

# In another terminal, run tests
python test_agent.py
```

The test suite covers:
- Basic greeting scenarios
- Various booking conversation flows
- Edge cases and error handling
- API endpoint functionality
- Complete conversation workflows

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for the LLM | Required |
| `GOOGLE_CALENDAR_CREDENTIALS_FILE` | Path to Google credentials | `credentials.json` |
| `GOOGLE_CALENDAR_TOKEN_FILE` | Path to token file | `token.json` |
| `FASTAPI_HOST` | Backend host | `localhost` |
| `FASTAPI_PORT` | Backend port | `8000` |
| `STREAMLIT_PORT` | Frontend port | `8501` |
| `TIMEZONE` | Default timezone | `America/New_York` |

### Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the JSON file as `credentials.json`
5. Place `credentials.json` in the project root directory

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check if all dependencies are installed: `pip install -r requirements.txt`
- Verify OpenAI API key is set in `.env` file
- Ensure port 8000 is not in use

**Google Calendar authentication fails:**
- Verify `credentials.json` is in the project root
- Check if Google Calendar API is enabled in Google Cloud Console
- Delete `token.json` and re-authenticate if needed

**Frontend can't connect to backend:**
- Ensure backend is running on `http://localhost:8000`
- Check firewall settings
- Verify API endpoints are accessible: `curl http://localhost:8000/health`

**Agent responses are poor:**
- Verify OpenAI API key is valid and has sufficient credits
- Check internet connection
- Review conversation context and history

## Deployment

### Local Development
The application is configured for local development by default.

### Production Deployment
For production deployment:

1. **Environment Setup:**
   - Set production environment variables
   - Use a proper database for session storage
   - Configure proper CORS origins
   - Set up SSL/TLS certificates

2. **Backend Deployment:**
   - Use a production WSGI server like Gunicorn
   - Set up reverse proxy with Nginx
   - Configure logging and monitoring

3. **Frontend Deployment:**
   - Deploy Streamlit app to Streamlit Cloud or similar
   - Update API base URL to production backend

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python test_agent.py`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **OpenAI** for the GPT models
- **LangChain/LangGraph** for the agent framework
- **Google** for the Calendar API
- **FastAPI** for the backend framework
- **Streamlit** for the frontend framework
