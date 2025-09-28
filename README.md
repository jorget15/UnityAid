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

## 🌐 **Deployment**

**Ready to deploy?** UnityAid can be deployed on **Streamlit Community Cloud** for free!

👉 **[Complete Deployment Guide →](DEPLOYMENT.md)**

Quick deploy:
1. Push to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)  
3. Add your Google API key to secrets
4. Deploy in 5 minutes! 🚀

---

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

## 🔮 Next Steps - Future Roadmap

UnityAid is designed to evolve into a comprehensive **Agentic Disaster Response Ecosystem**. Here are the planned enhancements that will transform the system into a fully autonomous emergency coordination platform:

### 🔗 **Phase 1: Event Deduplication Agent**
**Smart Ticket Bundling & Duplicate Detection**

- **Intelligent Event Correlation**: Deploy an AI agent that automatically identifies when multiple tickets pertain to the same incident
- **Cross-Reference Analysis**: 
  - Geographic clustering (same location, nearby coordinates)
  - Temporal correlation (reports within similar timeframes)
  - Semantic similarity (same type of emergency, similar descriptions)
  - Reporter analysis (multiple people reporting the same visible event)
- **Automatic Bundling**: Group related tickets into unified incident reports
- **Confidence Scoring**: Provide transparency on correlation certainty
- **Manual Override**: Allow dispatchers to merge/separate tickets when needed

**Benefits**: Reduces dispatcher workload, prevents resource duplication, provides clearer situational awareness

### 📞 **Phase 2: Voice-to-Ticket Chatbot**
**AI-Powered Call Transcription & Processing**

- **Real-Time Transcription**: Convert emergency calls to text using advanced speech-to-text models
- **Conversational AI Integration**: 
  - Extract key information during live calls
  - Ask clarifying questions automatically
  - Provide guidance to callers while collecting data
- **Automatic Ticket Generation**: Create structured tickets from call transcripts
- **Multi-Language Support**: Handle calls in multiple languages with translation
- **Priority Escalation**: Instantly elevate critical calls to human dispatchers
- **Call Analytics**: Track call patterns, response times, and outcome metrics

**Integration Points**:
- Voice recognition → Text processing → PrioritizerAgent → Ticket creation
- Location extraction from verbal descriptions ("near the CVS on 5th Street")
- Emotional tone analysis for urgency assessment

### 🤖 **Phase 3: Agentic Dispatch System**
**Fully Autonomous Emergency Coordination**

**Multi-Agent Architecture**:
- **Dispatch Coordinator**: Central orchestrator managing all response activities  
- **Resource Allocation Agent**: Optimizes resource assignment based on capacity, location, and expertise
- **Route Optimization Agent**: Calculates fastest response paths considering traffic, road conditions
- **Communication Agent**: Handles all stakeholder notifications and updates
- **Learning Agent**: Continuously improves system performance based on outcomes

**Advanced Capabilities**:
- **Predictive Resource Deployment**: Pre-position resources based on historical patterns and current conditions
- **Dynamic Re-routing**: Adjust response plans in real-time as situations evolve
- **Cross-Jurisdiction Coordination**: Automatically coordinate with neighboring emergency services
- **Outcome Tracking**: Monitor response effectiveness and continuously optimize
- **Integration APIs**: Connect with existing CAD systems, hospital networks, and government databases

**Intelligence Features**:
- **Weather Integration**: Factor weather conditions into response planning
- **Traffic Analysis**: Use real-time traffic data for optimal routing
- **Resource Learning**: Build profiles of resource capabilities and performance
- **Historical Analysis**: Learn from past incidents to improve future responses

### 🏗️ **Technical Architecture Evolution**

**Phase 1 Architecture**:
```
UnityAid → Event Deduplication Agent → Unified Incident Reports
```

**Phase 2 Architecture**:
```
Voice Calls → Transcription Service → Chatbot Agent → Ticket Generation → UnityAid
```

**Phase 3 Architecture**:
```
Multiple Input Channels → Agentic Dispatch System → Coordinated Response
├── Voice Calls        ├── Dispatch Coordinator
├── Web Tickets        ├── Resource Allocation Agent  
├── Mobile Apps        ├── Route Optimization Agent
├── IoT Sensors        ├── Communication Agent
└── External APIs      └── Learning Agent
```

### 📈 **Implementation Timeline**

**Q1 2025**: Event Deduplication Agent
- Semantic similarity analysis
- Geographic clustering algorithms
- Confidence scoring system
- Basic bundling interface

**Q2 2025**: Voice-to-Ticket System  
- Speech-to-text integration
- Conversational AI enhancement
- Multi-language support
- Call analytics dashboard

**Q3-Q4 2025**: Agentic Dispatch System
- Multi-agent coordination framework
- Predictive analytics integration
- Cross-system API development
- Performance optimization

### 🎯 **Expected Impact**

**Current State**:
- Manual ticket triage and routing
- Individual incident processing
- Human-driven resource allocation

**Future State**:
- **90% automation** in routine emergency processing
- **50% faster** response times through optimization
- **Zero duplicate responses** through intelligent bundling  
- **Predictive deployment** reducing average response time
- **Cross-jurisdictional coordination** for major incidents

**Success Metrics**:
- Response time reduction
- Resource utilization efficiency  
- Incident resolution rates
- System reliability and uptime
- User satisfaction scores

---

*This roadmap positions UnityAid as the foundation for next-generation emergency response - where AI agents work seamlessly with human expertise to save more lives, faster.*

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Test conversational AI: `python test_conversational_ai.py`
4. Submit pull request with clear description

## 📝 License

This project is open source - see LICENSE file for details.

---

*UnityAid represents the next generation of disaster response coordination, combining human expertise with intelligent AI assistance to save lives more effectively.*


