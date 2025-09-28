# UnityAid — Disaster Response System 🆘

UnityAid is an intelligent disaster response coordination system built with Streamlit, featuring AI-powered ticket triage with **conversational priority classification**.

## 🌟 Key Features

### 🤖 **Conversational AI Priority Classification** (NEW!)
- Smart AI asks clarifying questions when confidence is below 70%
- Tailored questions based on emergency type (medical, safety, vulnerable populations)
- Dynamic priority adjustment based on additional context
- Transparent confidence scoring for quality assurance

### 📍 **Interactive Mapping**
- Click-to-pin location selection using Folium maps
- Visual representation of reports and resources
- Real-time updates of incident locations

### 🎫 **Intelligent Ticket Management**
- AI-powered ticket composition from freeform descriptions
- Enhanced priority classification with 75%+ accuracy
- Manual ticket creation for specific scenarios
- Comprehensive ticket tracking and status updates

### 📊 **Live Dashboard**
- Real-time monitoring of all active tickets
- Priority-based sorting and filtering
- Resource capacity tracking
- Interactive data visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.12/3.13 recommended)
- Virtual environment (strongly recommended)

### Installation (Windows PowerShell)

1. **Clone and navigate to the project**:
```powershell
git clone https://github.com/your-repo/UnityAid.git
cd UnityAid
```

2. **Create and activate virtual environment**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

3. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

4. **Configure environment (optional but recommended)**:
```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env with your preferred text editor
notepad .env
```

**Important**: Add your Google AI API key to `.env` for enhanced features:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

5. **Run the application**:
```powershell
streamlit run app_streamlit.py
```

6. **Access the application**:
   - Open your browser to: http://localhost:8501
   - Start submitting tickets and managing disaster response!

## 💡 How the Conversational AI Works

### Example Workflow:

1. **Submit Description**: "Someone needs help"
   - AI Assessment: Priority 3/5, 60% confidence ❓
   
2. **AI Asks Questions**:
   - "Are people in immediate physical danger?"
   - "How many people are affected?"
   - "Is this situation getting worse over time?"
   
3. **High Urgency Answers**:
   - "Yes, trapped under debris"
   - "Three people including a child"
   - "Structure is becoming unstable"
   
4. **Updated Classification**: Priority 5/5, 90% confidence ✅

### Smart Question Generation:
- **Medical emergencies**: Consciousness, breathing, mobility
- **Safety situations**: Immediate danger, accessibility, scope  
- **Vulnerable groups**: Children, elderly, pregnant individuals
- **Resource needs**: Timeline, alternatives, deterioration rate

See [CONVERSATIONAL_AI.md](CONVERSATIONAL_AI.md) for detailed documentation.

## 🏗️ Architecture

### Core Components:
- **Streamlit Frontend**: Interactive web interface with real-time updates
- **PrioritizerAgent**: AI-powered priority classification with conversation support
- **Interactive Maps**: Folium-based location selection and visualization  
- **Session Management**: Persistent data storage across user interactions
- **Enhanced Heuristics**: Pattern matching with 75%+ accuracy

### File Structure:
```
UnityAid/
├── app_streamlit.py              # Main Streamlit application
├── PrioritizerAgent/
│   ├── agent.py                  # Google ADK agent definition
│   └── prioritizer_integration.py # Integration & conversation logic
├── requirements.txt              # Python dependencies  
├── CONVERSATIONAL_AI.md          # Detailed AI documentation
└── test_conversational_ai.py     # Testing script
```

## 🧪 Testing the Conversational AI

Run the test script to see the AI in action:

```powershell
# Test various scenarios
python test_conversational_ai.py

# Or test specific cases interactively
python -c "
from PrioritizerAgent.prioritizer_integration import classify_with_conversation
result = classify_with_conversation('Someone needs help')
print(f'Priority: {result[\"priority\"]}/5, Confidence: {result[\"confidence\"]:.1%}')
if result.get('clarifying_questions'):
    print('Questions:', result['clarifying_questions'])
"
```

### Test Results:
- ✅ **Clear emergencies**: 90%+ confidence, no questions needed
- ❓ **Ambiguous cases**: 60-70% confidence, 2-4 targeted questions  
- ✅ **Post-Q&A**: Typically 80-95% confidence with improved accuracy
- 📊 **Priority adjustments**: Range from -2 to +2 based on additional context

## 🎯 Usage Examples

### High-Confidence Case (No Questions):
```
Input: "Person is unconscious and not breathing at downtown intersection"
Result: Priority 5/5, 90% confidence → Ticket created immediately
```

### Low-Confidence Case (Questions Asked):
```
Input: "Someone needs help"
Initial: Priority 3/5, 60% confidence
Questions: 
  1. Are people in immediate physical danger?
  2. How many people are affected?
  3. Is this situation getting worse over time?

High-urgency answers → Priority 5/5, 90% confidence
Low-urgency answers → Priority 2/5, 80% confidence
```

## 🔧 Configuration

### Environment Variables:
- `GOOGLE_API_KEY`: Optional Google AI API key for enhanced classification
- `GOOGLE_MODEL`: Model to use (default: "gemini-1.5-flash")

### Customization:
- **Confidence threshold**: Adjust in `PrioritizerConversation.confidence_threshold` (default: 0.7)
- **Question limits**: Modify in `get_clarifying_questions()` method
- **Priority scales**: Update heuristic keywords in `enhanced_priority_classification()`

## 📊 Features by Tab

### 🎫 Ticket Agent Tab:
- **Interactive AI Composition**: Freeform input → structured ticket
- **Conversational Questions**: Smart follow-ups for low-confidence cases
- **Location Selection**: Click-to-pin on interactive map
- **Report Linking**: Connect tickets to existing incident reports

### ✏️ Manual Ticket Tab:
- **Direct Entry**: Traditional form-based ticket creation
- **Manual Priority**: Override AI suggestions when needed
- **Structured Input**: Title, description, priority, status fields

### 📋 View Tickets Tab:
- **Active Monitoring**: Real-time list of all tickets
- **Priority Sorting**: Organize by urgency and status
- **Status Management**: Update ticket progress
- **Location Display**: GPS coordinates and map references

### 📊 Dashboard Tab:
- **Live Metrics**: Real-time statistics and trends
- **Resource Tracking**: Monitor capacity and allocation
- **Visual Analytics**: Charts and graphs for decision support

## 🚀 Advanced Features

### Smart Question Generation:
The AI generates contextually relevant questions based on detected patterns:

```python
Medical Emergency Detected:
- "Is the person conscious and responsive?"
- "Are they having difficulty breathing?"
- "Is there any bleeding? If yes, how severe?"

Safety Situation Detected:  
- "Are people in immediate physical danger?"
- "Is the location safe for responders to access?"
- "How many people are affected?"

Vulnerable Population Detected:
- "Are there children, elderly, or pregnant individuals involved?"
- "Do they have access to necessary medications?"
```

### Priority Adjustment Logic:
- **Medical keywords**: +1-2 priority boost
- **Danger indicators**: +1-3 priority boost  
- **Vulnerable populations**: +1 priority boost
- **Stability indicators**: -1 priority reduction
- **Resource availability**: Context-dependent adjustment

## ⚙️ Environment Configuration

UnityAid supports various configuration options through environment variables. Copy `.env.example` to `.env` and customize as needed:

### 🔑 **Essential Settings**
```env
# Google AI API Key (strongly recommended)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-1.5-flash

# Conversational AI Settings
PRIORITIZER_CONFIDENCE_THRESHOLD=0.7  # Lower = more questions
MAX_QUESTIONS_PER_SESSION=4
```

### 📊 **Feature Toggles**
```env
# Enable/disable major features
ENABLE_CONVERSATIONAL_AI=true
ENABLE_ENHANCED_TITLES=true
ENABLE_INTERACTIVE_MAPS=true
ENABLE_ANALYTICS=true
```

### 🔧 **Application Settings**
```env
# Environment and debugging
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO

# Server configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### 🚨 **Getting Your Google AI API Key**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file
5. Restart the application

**Note**: The app works without an API key using fallback heuristics, but Google AI provides significantly better title generation and classification accuracy.

## 🔍 Troubleshooting

### Common Issues:

**Q: AI questions not appearing**
- A: Check that confidence is below 70% - clear emergencies skip questions
- Verify PrioritizerAgent module is properly imported

**Q: Maps not loading**  
- A: Ensure folium and streamlit-folium are installed
- Check browser console for JavaScript errors

**Q: Tickets not saving**
- A: Verify all required fields are completed
- Check session state persistence

**Q: Low AI confidence consistently**
- A: Provide more detailed initial descriptions
- Consider adjusting confidence threshold in config

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Test conversational AI: `python test_conversational_ai.py`
4. Submit pull request with clear description

## 📝 License

This project is open source - see LICENSE file for details.

---

*UnityAid represents the next generation of disaster response coordination, combining human expertise with intelligent AI assistance to save lives more effectively.*
      - '8000:8000'
    depends_on:
      - redis
  categorizer:
    build: .
    command: python categorizer_agent.py
    depends_on:
      - backend
      - redis
  matcher:
    build: .
    command: python matcher_agent.py
    depends_on:
      - backend
      - redis
```

You can adapt the backend to use Redis pub/sub and bridge A2A via Redis; if you want I can scaffold that bridge so the backend uses Redis and the SSE relays messages from Redis to clients.

## Logs

The app writes rotating logs to `logs/unityaid.log`. If you don't see logs, ensure the `logs/` directory exists and the process user can write to it.

## Troubleshooting

- Port already in use: stop other uvicorn processes or change `--port`.
- SSE not receiving events: SSE is in-memory and per-process; ensure you're connected to the same process that runs the background agent (don't use multiple uvicorn workers with `--workers > 1` unless you switch to an external pub/sub).
- If endpoints return 404, ensure the server is running and you are using the correct host/port.

## Next steps / optional

- Wire persistent storage for reports/resources
- Replace in-memory pub/sub with Redis pub/sub for multi-worker SSE
- Add tests that validate enqueue -> agent matching -> event emission


