# 🤖 AI Calendar Booking Agent

A conversational AI agent that assists users in booking appointments on Google Calendar using natural language interactions.

## 🌟 Features

- 🤖 **Natural Language Processing** - Understands booking requests in plain English
- 📅 **Smart Calendar Integration** - Real-time availability checking and booking
- 💬 **Conversational Interface** - Multi-turn conversations with context awareness
- 🎨 **Beautiful UI** - Clean Streamlit interface with color-coded messages
- 🛡️ **Robust Error Handling** - Graceful fallbacks and edge case management
- 🔧 **Flexible Architecture** - Works with or without external APIs

## 🚀 Live Demo

### **🌐 Deployed Version**
- **Frontend:** [Coming Soon - Deploy to get public URL]
- **Backend API:** [Coming Soon - Deploy to get public URL]

### **💻 Local Development**
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-calendar-booking-agent.git
cd ai-calendar-booking-agent

# Install dependencies
pip install -r requirements.txt

# Start the application
python start_app.py

# Access at http://localhost:8501
```

## 🎯 Example Conversations

```
👤 User: "Hey, I want to schedule a call for tomorrow afternoon."
🤖 Agent: "I'd be happy to help! I found some available slots for tomorrow afternoon..."

👤 User: "Do you have any free time this Friday?"
🤖 Agent: "Let me check Friday's availability for you..."

👤 User: "Book a meeting between 3-5 PM next week."
🤖 Agent: "I found several options for next week between 3-5 PM..."
```

## 🏗️ Architecture

```
Frontend (Streamlit) ←→ Backend (FastAPI) ←→ Agent (LangGraph/Simple)
                                          ↓
                                    Calendar Service (Mock/Google)
```

## 📦 Tech Stack

- **Backend:** FastAPI, Python 3.10+
- **Agent:** LangGraph, LangChain, OpenAI GPT
- **Frontend:** Streamlit
- **Calendar:** Google Calendar API (with mock fallback)
- **Deployment:** Docker, Railway, Render

## 🚀 Quick Start

### Option 1: One-Command Launch
```bash
python start_app.py
```

### Option 2: Manual Setup
```bash
# Terminal 1: Backend
python run_backend.py

# Terminal 2: Frontend
python run_frontend_colored.py
```

### Option 3: Docker
```bash
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables
```bash
# Optional: For enhanced AI capabilities
OPENAI_API_KEY=your_openai_api_key

# Optional: For real Google Calendar integration
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json

# Deployment settings
API_BASE_URL=http://localhost:8000
TIMEZONE=America/New_York
```

### Google Calendar Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to project root

## 🧪 Testing

```bash
# Run comprehensive tests
python test_agent.py

# Quick functionality test
python quick_test.py

# Interactive demo
python demo.py
```

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── agent/               # LangGraph agent implementation
│   ├── calendar/            # Calendar integration (Google + Mock)
│   └── models/              # Pydantic data models
├── frontend/
│   ├── app_colored.py       # Main Streamlit interface
│   ├── app.py               # Alternative interface
│   └── app_v2.py            # Chat elements interface
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker deployment
└── README.md               # This file
```

## 🌐 Deployment

### Railway (Recommended)
1. Fork this repository
2. Connect to [Railway](https://railway.app)
3. Deploy backend and frontend services
4. Set environment variables

### Streamlit Cloud (Frontend Only)
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy `frontend/app_colored.py`

### Render (Free Tier)
1. Fork this repository
2. Connect to [Render](https://render.com)
3. Use provided `render.yaml` configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain/LangGraph for agent framework
- Google for Calendar API
- Streamlit for the amazing UI framework

---

**⭐ Star this repo if you found it helpful!**
