# UnityAid - Streamlit Version
import streamlit as st
import uuid
import math
import json
import os
import time
from typing import Optional, Literal, Dict, List
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
import folium
from streamlit_folium import st_folium

# Configure page
st.set_page_config(
    page_title="UnityAid - Disaster Response",
    page_icon="🆘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Type definitions
Category = Literal["food", "water", "medical", "shelter", "other"]
TicketStatus = Literal["open", "in_progress", "closed"]

@dataclass
class Report:
    id: str
    description: str
    lat: float
    lon: float
    urgency: int
    category: Category = "other"
    matched_resource_id: Optional[str] = None

@dataclass
class Resource:
    id: str
    name: str
    type: Category
    lat: float
    lon: float
    capacity: int
    notes: Optional[str] = None

@dataclass
class Ticket:
    id: str
    title: str
    description: str
    status: TicketStatus
    priority: int
    created_at: float
    qualified_priority: Optional[int] = None
    qualified_by: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    report_id: Optional[str] = None

def seed_resources():
    resources_data = [
        Resource(id="rc1", name="NGO Food Hub", type="food", lat=25.775, lon=-80.20, capacity=150),
        Resource(id="rc2", name="Water Station North", type="water", lat=25.810, lon=-80.19, capacity=300),
        Resource(id="rc3", name="Shelter @ HighSchool", type="shelter", lat=25.740, lon=-80.22, capacity=120),
        Resource(id="rc4", name="Pop-up Clinic", type="medical", lat=25.770, lon=-80.18, capacity=40, notes="Basic meds"),
    ]
    for r in resources_data:
        st.session_state.resources[r.id] = r

# Initialize session state
def init_session_state():
    if 'reports' not in st.session_state:
        st.session_state.reports = {}
    if 'resources' not in st.session_state:
        st.session_state.resources = {}
    if 'tickets' not in st.session_state:
        st.session_state.tickets = {}
    if 'queue' not in st.session_state:
        st.session_state.queue = deque(maxlen=1000)
    if 'initialized' not in st.session_state:
        seed_resources()
        st.session_state.initialized = True

# Keywords for categorization
KEYWORDS = {
    "medical": ["insulin", "injury", "bleeding", "medicine", "asthma", "diabetes", "clinic", "doctor"],
    "water": ["water", "thirst", "dehydrated", "bottles"],
    "food": ["food", "hungry", "meal", "grocery", "hunger"],
    "shelter": ["shelter", "roof", "evacuate", "evacuation", "homeless"],
}

def categorize(text: str) -> Category:
    t = text.lower()
    for cat, words in KEYWORDS.items():
        if any(w in t for w in words):
            return cat  # type: ignore
    return "other"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    h = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

def match_resource(rep: Report) -> Optional[Resource]:
    resources = st.session_state.resources
    cand = [r for r in resources.values() if r.capacity > 0 and (r.type == rep.category or rep.category == "other")]
    if not cand:
        cand = [r for r in resources.values() if r.capacity > 0]
    if not cand:
        return None
    return min(cand, key=lambda r: haversine(rep.lat, rep.lon, r.lat, r.lon))

def create_interactive_map(center_lat=25.77, center_lon=-80.19, zoom=10, key="map"):
    """Create an interactive folium map with click-to-pin functionality."""
    # Create base map centered on Miami (default disaster area)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    
    # Add existing reports as markers
    for report in st.session_state.reports.values():
        popup_text = f"""
        <b>Report {report.id}</b><br>
        Category: {report.category}<br>
        Urgency: {report.urgency}/5<br>
        Description: {report.description[:50]}...
        """
        folium.Marker(
            location=[report.lat, report.lon],
            popup=folium.Popup(popup_text, max_width=200),
            icon=folium.Icon(color='red', icon='exclamation-sign')
        ).add_to(m)
    
    # Add existing resources as markers
    for resource in st.session_state.resources.values():
        popup_text = f"""
        <b>{resource.name}</b><br>
        Type: {resource.type}<br>
        Capacity: {resource.capacity}<br>
        {resource.notes or ''}
        """
        folium.Marker(
            location=[resource.lat, resource.lon],
            popup=folium.Popup(popup_text, max_width=200),
            icon=folium.Icon(color='green', icon='home')
        ).add_to(m)
    
    # Add a marker for the currently selected location if it exists
    session_key = f"{key}_selected_lat"
    if session_key in st.session_state and st.session_state[session_key]:
        folium.Marker(
            location=[st.session_state[session_key], st.session_state[f"{key}_selected_lon"]],
            popup="Selected Location",
            icon=folium.Icon(color='blue', icon='star')
        ).add_to(m)
    
    # Display the map and capture click events
    map_data = st_folium(m, key=key, width=700, height=400)
    
    # Extract coordinates from last clicked location and store in session state
    if map_data["last_clicked"]:
        st.session_state[f"{key}_selected_lat"] = map_data["last_clicked"]["lat"]
        st.session_state[f"{key}_selected_lon"] = map_data["last_clicked"]["lng"]
        st.rerun()
    
    # Return the stored coordinates
    selected_lat = st.session_state.get(f"{key}_selected_lat")
    selected_lon = st.session_state.get(f"{key}_selected_lon")
    
    return selected_lat, selected_lon, map_data
    resources_data = [
        Resource(id="rc1", name="NGO Food Hub", type="food", lat=25.775, lon=-80.20, capacity=150),
        Resource(id="rc2", name="Water Station North", type="water", lat=25.810, lon=-80.19, capacity=300),
        Resource(id="rc3", name="Shelter @ HighSchool", type="shelter", lat=25.740, lon=-80.22, capacity=120),
        Resource(id="rc4", name="Pop-up Clinic", type="medical", lat=25.770, lon=-80.18, capacity=40, notes="Basic meds"),
    ]
    for r in resources_data:
        st.session_state.resources[r.id] = r

def ai_qualify_urgency(text: str, use_conversation: bool = True) -> dict:
    """Return priority classification result with potential follow-up questions."""
    
    # Try to use the PrioritizerAgent first with conversation support
    try:
        import sys
        from pathlib import Path
        prioritizer_path = Path(__file__).parent / "PrioritizerAgent"
        sys.path.append(str(prioritizer_path))
        
        if use_conversation:
            from prioritizer_integration import classify_with_conversation
            result = classify_with_conversation(text)
        else:
            from prioritizer_integration import classify_ticket_priority
            result = classify_ticket_priority(text)
            
        return {
            'priority': result['priority'],
            'source': f"PrioritizerAgent ({result['confidence']:.2f})",
            'confidence': result['confidence'],
            'needs_clarification': result.get('needs_clarification', False),
            'clarifying_questions': result.get('clarifying_questions', []),
            'conversation_id': result.get('conversation_id')
        }
        
    except Exception as e:
        # Fallback to original heuristic if PrioritizerAgent fails
        print(f"PrioritizerAgent not available, using fallback: {e}")
        pass
    
    # Original heuristic fallback
    t = (text or "").lower()
    score = 3
    
    # Heuristic keywords
    critical_kw = ["life-threatening", "unconscious", "not breathing", "cardiac", "hemorrhage", 
                   "severe bleeding", "child missing", "trapped", "collapsed", "hurricane", "wildfire"]
    high_kw = ["urgent", "immediately", "critical", "asap", "help now", "injury", "insulin", 
               "diabetic", "asthma", "pregnant", "baby", "elderly", "no water", "dehydration", 
               "no food", "no shelter"]
    low_kw = ["minor", "low", "non-urgent", "later", "when possible"]
    
    hits = 0
    for w in critical_kw:
        if w in t:
            hits += 2
    for w in high_kw:
        if w in t:
            hits += 1
    for w in low_kw:
        if w in t:
            hits -= 1
    
    # Map hits to priority
    if hits >= 4:
        score = 5
    elif hits >= 2:
        score = 4
    elif hits <= -1:
        score = 2
    else:
        score = 3
    
    # Try Google Generative AI if available
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)
            prompt = (
                "You are a disaster response triage assistant. "
                "Classify the urgency of the following ticket from 1 (lowest) to 5 (critical). "
                "Return only a single integer 1-5.\n\nText: " + (text or "")
            )
            resp = model.generate_content(prompt)
            content = resp.text.strip() if hasattr(resp, 'text') else str(resp).strip()
            parsed = int(''.join(ch for ch in content if ch.isdigit())[:1] or '3')
            parsed = max(1, min(5, parsed))
            return {
                'priority': parsed, 
                'source': f"google:{model_name}",
                'confidence': 0.75,
                'needs_clarification': False,
                'clarifying_questions': []
            }
    except Exception:
        pass
    
    return {
        'priority': score, 
        'source': "heuristic",
        'confidence': 0.65,
        'needs_clarification': False,
        'clarifying_questions': []
    }

def ai_compose_ticket(raw_input: str, report: Optional[Report] = None) -> dict:
    """Compose a ticket dict with title, description, priority."""
    text = (raw_input or "").strip()
    lower = text.lower()
    title = "Assistance needed"
    
    # Try Google Generative AI for title
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)
            prompt = (
                "Create a concise, action-oriented title (max 6 words) for a disaster response ticket.\n"
                "Only return the title, no punctuation beyond what's necessary.\n\nText: " + (raw_input or "")
            )
            resp = model.generate_content(prompt)
            gen_title = resp.text.strip() if hasattr(resp, 'text') else None
            if gen_title:
                title = gen_title.split('\n')[0][:80]
            source = f"google:{model_name}"
        else:
            source = "heuristic"
    except Exception:
        source = "heuristic"
    
    if source == "heuristic":
        if any(w in lower for w in ["water", "dehydration", "thirst"]):
            title = "Water assistance needed"
        elif any(w in lower for w in ["food", "hunger", "meals", "supplies"]):
            title = "Food assistance needed"
        elif any(w in lower for w in ["injury", "medical", "insulin", "asthma", "medicine", "hospital"]):
            title = "Medical assistance required"
        elif any(w in lower for w in ["shelter", "housing", "evacuate", "evacuation", "homeless"]):
            title = "Shelter assistance needed"
    
    urgency_result = ai_qualify_urgency(text)
    desc = text
    if report and report.description and (len(text) < 10 or report.description not in text):
        desc = f"{text}\nLinked report: {report.id} — {report.description}"
    
    return {
        "title": title,
        "description": desc,
        "priority": urgency_result['priority'],
        "qualified_priority": urgency_result['priority'],
        "qualified_by": urgency_result['source'],
        "confidence": urgency_result['confidence'],
        "needs_clarification": urgency_result['needs_clarification'],
        "clarifying_questions": urgency_result['clarifying_questions'],
        "conversation_id": urgency_result.get('conversation_id')
    }

def process_queue():
    """Process queued reports for categorization and matching."""
    if st.session_state.queue:
        rid = st.session_state.queue.popleft()
        rep = st.session_state.reports.get(rid)
        if rep:
            rep.category = categorize(rep.description)
            res = match_resource(rep)
            if res:
                rep.matched_resource_id = res.id
                res.capacity = max(res.capacity - 1, 0)
                st.session_state.resources[res.id] = res
                st.session_state.reports[rid] = rep
                return True
    return False

# Initialize session state
init_session_state()

# Sidebar navigation
st.sidebar.title("🆘 UnityAid")
page = st.sidebar.selectbox("Navigate", [
    "Dashboard", 
    "View Reports", 
    "Resources", 
    "Submit a Ticket",
    "Map View"
])

if page == "Dashboard":
    st.title("UnityAid Dashboard")
    
    # Process queue automatically
    if st.button("🔄 Process Queue", help="Process pending reports"):
        processed = process_queue()
        if processed:
            st.success("✅ Processed a report from queue!")
            st.rerun()
        else:
            st.info("Queue is empty")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Reports", len(st.session_state.reports))
    with col2:
        st.metric("Resources", len(st.session_state.resources))
    with col3:
        st.metric("Tickets", len(st.session_state.tickets))
    with col4:
        st.metric("Queue Size", len(st.session_state.queue))
    
    # Recent activity
    st.subheader("Recent Reports")
    if st.session_state.reports:
        reports_list = list(st.session_state.reports.values())
        for report in sorted(reports_list, key=lambda x: x.id, reverse=True)[:5]:
            with st.expander(f"Report {report.id} - {report.category.title()}"):
                st.write(f"**Description:** {report.description}")
                st.write(f"**Location:** ({report.lat:.3f}, {report.lon:.3f})")
                st.write(f"**Urgency:** {report.urgency}/5")
                if report.matched_resource_id:
                    resource = st.session_state.resources.get(report.matched_resource_id)
                    if resource:
                        st.success(f"✅ Matched to: {resource.name}")
                else:
                    st.warning("❌ No resource matched")
    else:
        st.info("No reports yet")

elif page == "View Reports":
    st.title("All Reports")
    
    if st.session_state.reports:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox("Filter by Category", 
                                         ["All"] + list(KEYWORDS.keys()) + ["other"])
        with col2:
            urgency_filter = st.selectbox("Filter by Urgency", 
                                        ["All", "5-Critical", "4-High", "3-Medium", "2-Low", "1-Minimal"])
        
        # Display reports
        reports_list = list(st.session_state.reports.values())
        
        # Apply filters
        if category_filter != "All":
            reports_list = [r for r in reports_list if r.category == category_filter]
        
        if urgency_filter != "All":
            urgency_num = int(urgency_filter[0])
            reports_list = [r for r in reports_list if r.urgency == urgency_num]
        
        for report in reports_list:
            with st.expander(f"Report {report.id} - {report.category.title()} - Urgency {report.urgency}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Description:** {report.description}")
                    st.write(f"**Category:** {report.category}")
                    st.write(f"**Urgency:** {report.urgency}/5")
                with col2:
                    st.write(f"**Location:** ({report.lat:.6f}, {report.lon:.6f})")
                    if report.matched_resource_id:
                        resource = st.session_state.resources.get(report.matched_resource_id)
                        if resource:
                            st.success(f"✅ Matched to: {resource.name}")
                    else:
                        st.warning("❌ No resource matched")
    else:
        st.info("No reports submitted yet")

elif page == "Resources":
    st.title("Available Resources")
    
    for resource in st.session_state.resources.values():
        with st.expander(f"{resource.name} ({resource.type.title()})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {resource.type}")
                st.write(f"**Capacity:** {resource.capacity}")
                if resource.notes:
                    st.write(f"**Notes:** {resource.notes}")
            with col2:
                st.write(f"**Location:** ({resource.lat:.6f}, {resource.lon:.6f})")
                
            # Capacity indicator
            if resource.capacity > 100:
                st.success(f"High capacity: {resource.capacity} available")
            elif resource.capacity > 50:
                st.warning(f"Medium capacity: {resource.capacity} available")
            elif resource.capacity > 0:
                st.error(f"Low capacity: {resource.capacity} available")
            else:
                st.error("No capacity available")

elif page == "Submit a Ticket":
    st.title("🎫 Submit a Ticket")
    
    # Tabs for different ticket operations
    tab1, tab2, tab3 = st.tabs(["Ticket Agent", "Manual Ticket", "View Tickets"])
    
    with tab1:
        st.subheader("AI Agent Ticket Composer")
        
        # Location selection outside the form
        st.write("**📍 Click on the map to set location (optional)**")
        agent_clicked_lat, agent_clicked_lon, agent_map_data = create_interactive_map(key="agent_map")
        
        # Show selected coordinates
        if agent_clicked_lat and agent_clicked_lon:
            st.success(f"📍 Selected location: ({agent_clicked_lat:.6f}, {agent_clicked_lon:.6f})")
        else:
            st.info("Click on the map to select a location for this ticket")
        
        # Add button to clear selection
        if st.button("🗑️ Clear Location", key="clear_agent_location"):
            if "agent_map_selected_lat" in st.session_state:
                del st.session_state["agent_map_selected_lat"]
            if "agent_map_selected_lon" in st.session_state:
                del st.session_state["agent_map_selected_lon"]
            st.rerun()
        
        with st.form("agent_compose"):
            raw_input = st.text_area("Describe the situation", 
                                    placeholder="Freeform description that AI will convert to a structured ticket")
            
            # Optional report linking
            report_options = ["None"] + list(st.session_state.reports.keys())
            linked_report = st.selectbox("Link to Report (optional)", report_options, key="agent_report")
            
            composed = st.form_submit_button("🤖 Compose Ticket with AI", type="primary")
            
            if composed and raw_input:
                # Get linked report if selected
                report = st.session_state.reports.get(linked_report) if linked_report != "None" else None
                
                # AI compose
                composed_data = ai_compose_ticket(raw_input, report)
                
                # Check if we need clarification
                if composed_data.get('needs_clarification', False) and composed_data.get('clarifying_questions'):
                    # Store the initial data for later use
                    st.session_state['pending_ticket'] = {
                        'raw_input': raw_input,
                        'report': report,
                        'composed_data': composed_data,
                        'final_lat': agent_clicked_lat,
                        'final_lon': agent_clicked_lon,
                        'linked_report': linked_report
                    }
                    st.rerun()  # Refresh to show questions
                else:
                    # Use report location if not provided, otherwise use clicked location
                    final_lat = agent_clicked_lat
                    final_lon = agent_clicked_lon
                    if not agent_clicked_lat and not agent_clicked_lon and report:
                        final_lat = report.lat
                        final_lon = report.lon
                    
                    tid = str(uuid.uuid4())
                    ticket = Ticket(
                        id=tid,
                        title=composed_data["title"],
                        description=composed_data["description"],
                        status="open",
                        priority=composed_data["priority"],
                        created_at=time.time(),
                        qualified_priority=composed_data["qualified_priority"],
                        qualified_by=composed_data["qualified_by"],
                        lat=final_lat,
                        lon=final_lon,
                        report_id=linked_report if linked_report != "None" else None
                    )
                    
                    st.session_state.tickets[tid] = ticket
                    
                    st.success(f"🤖 AI-composed ticket created: {tid}")
                    st.info(f"**Generated Title:** {composed_data['title']}")
                    st.info(f"**AI Priority:** {composed_data['qualified_priority']} (via {composed_data['qualified_by']})")
                    confidence = composed_data.get('confidence', 0)
                    if confidence < 0.7:
                        st.warning(f"⚠️ AI confidence was low ({confidence:.2f}). Consider reviewing the priority.")
        
        # Handle follow-up questions if needed
        if 'pending_ticket' in st.session_state:
            st.divider()
            st.subheader("🤔 AI needs more information")
            
            pending = st.session_state['pending_ticket']
            composed_data = pending['composed_data']
            
            st.info(f"**Current AI assessment:** Priority {composed_data['priority']} with {composed_data['confidence']:.1%} confidence")
            st.info("Please answer the following questions to help improve the priority classification:")
            
            # Display questions and collect answers
            qa_pairs = []
            for i, question in enumerate(composed_data['clarifying_questions']):
                answer = st.text_input(f"Q{i+1}: {question}", key=f"qa_{i}")
                if answer.strip():
                    qa_pairs.append((question, answer.strip()))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Submit Answers", type="primary"):
                    if qa_pairs:
                        # Reclassify with the Q&A
                        try:
                            import sys
                            from pathlib import Path
                            prioritizer_path = Path(__file__).parent / "PrioritizerAgent"
                            sys.path.append(str(prioritizer_path))
                            
                            from prioritizer_integration import answer_questions_and_reclassify
                            
                            updated_result = answer_questions_and_reclassify(
                                pending['raw_input'], 
                                qa_pairs, 
                                composed_data.get('conversation_id')
                            )
                            
                            # Update composed data with new priority
                            composed_data.update({
                                'priority': updated_result['priority'],
                                'qualified_priority': updated_result['priority'],
                                'qualified_by': updated_result['source'],
                                'confidence': updated_result['confidence']
                            })
                            
                        except Exception as e:
                            st.error(f"Error reclassifying: {e}")
                        
                        # Use report location if not provided, otherwise use clicked location
                        final_lat = pending['final_lat']
                        final_lon = pending['final_lon']
                        if not final_lat and not final_lon and pending['report']:
                            final_lat = pending['report'].lat
                            final_lon = pending['report'].lon
                        
                        tid = str(uuid.uuid4())
                        ticket = Ticket(
                            id=tid,
                            title=composed_data["title"],
                            description=composed_data["description"] + f"\n\nAdditional Q&A:\n" + 
                                      "\n".join([f"Q: {q}\nA: {a}" for q, a in qa_pairs]),
                            status="open",
                            priority=composed_data["priority"],
                            created_at=time.time(),
                            qualified_priority=composed_data["qualified_priority"],
                            qualified_by=composed_data["qualified_by"],
                            lat=final_lat,
                            lon=final_lon,
                            report_id=pending['linked_report'] if pending['linked_report'] != "None" else None
                        )
                        
                        st.session_state.tickets[tid] = ticket
                        del st.session_state['pending_ticket']  # Clear pending state
                        
                        st.success(f"🤖 AI-composed ticket created: {tid}")
                        st.info(f"**Updated Priority:** {composed_data['qualified_priority']} (via {composed_data['qualified_by']})")
                        st.info(f"**Final Confidence:** {composed_data.get('confidence', 0):.1%}")
                        st.rerun()
                    else:
                        st.error("Please answer at least one question before submitting.")
            
            with col2:
                if st.button("⏭️ Skip Questions (Use Current Priority)"):
                    # Create ticket with original priority
                    final_lat = pending['final_lat']
                    final_lon = pending['final_lon']
                    if not final_lat and not final_lon and pending['report']:
                        final_lat = pending['report'].lat
                        final_lon = pending['report'].lon
                    
                    tid = str(uuid.uuid4())
                    ticket = Ticket(
                        id=tid,
                        title=composed_data["title"],
                        description=composed_data["description"],
                        status="open",
                        priority=composed_data["priority"],
                        created_at=time.time(),
                        qualified_priority=composed_data["qualified_priority"],
                        qualified_by=composed_data["qualified_by"],
                        lat=final_lat,
                        lon=final_lon,
                        report_id=pending['linked_report'] if pending['linked_report'] != "None" else None
                    )
                    
                    st.session_state.tickets[tid] = ticket
                    del st.session_state['pending_ticket']
                    
                    st.success(f"🤖 AI-composed ticket created: {tid}")
                    st.warning(f"⚠️ Used original priority {composed_data['priority']} with {composed_data.get('confidence', 0):.1%} confidence")
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel"):
                    del st.session_state['pending_ticket']
                    st.rerun()
    
    with tab2:
        st.subheader("Create New Ticket")
        
        # Location selection outside the form
        st.write("**📍 Click on the map to set location (optional)**")
        clicked_lat, clicked_lon, map_data = create_interactive_map(key="ticket_map")
        
        # Show selected coordinates
        if clicked_lat and clicked_lon:
            st.success(f"📍 Selected location: ({clicked_lat:.6f}, {clicked_lon:.6f})")
        else:
            st.info("Click on the map to select a location for this ticket")
        
        # Add button to clear selection
        if st.button("🗑️ Clear Location", key="clear_ticket_location"):
            if "ticket_map_selected_lat" in st.session_state:
                del st.session_state["ticket_map_selected_lat"]
            if "ticket_map_selected_lon" in st.session_state:
                del st.session_state["ticket_map_selected_lon"]
            st.rerun()
        
        with st.form("ticket_form"):
            title = st.text_input("Title", placeholder="Brief description of the issue")
            description = st.text_area("Description", placeholder="Detailed description")
            priority = st.select_slider("Priority", options=[1, 2, 3, 4, 5], value=3)
            
            # Link to existing report
            report_options = ["None"] + list(st.session_state.reports.keys())
            linked_report = st.selectbox("Link to Report (optional)", report_options)
            
            submitted = st.form_submit_button("Create Ticket", type="primary")
            
            if submitted and title and description:
                tid = str(uuid.uuid4())
                ai_score, source = ai_qualify_urgency(description)
                
                ticket = Ticket(
                    id=tid,
                    title=title,
                    description=description,
                    status="open",
                    priority=priority,
                    created_at=time.time(),
                    qualified_priority=ai_score,
                    qualified_by=source,
                    lat=clicked_lat,
                    lon=clicked_lon,
                    report_id=linked_report if linked_report != "None" else None
                )
                
                st.session_state.tickets[tid] = ticket
                st.success(f"✅ Ticket {tid} created! AI suggested priority: {ai_score} ({source})")
    
    with tab3:
        st.subheader("All Tickets")
        
        if st.session_state.tickets:
            for ticket in st.session_state.tickets.values():
                status_color = {"open": "🔴", "in_progress": "🟡", "closed": "🟢"}
                with st.expander(f"{status_color[ticket.status]} {ticket.title} (Priority: {ticket.priority})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {ticket.id}")
                        st.write(f"**Status:** {ticket.status}")
                        st.write(f"**Priority:** {ticket.priority}")
                        if ticket.qualified_priority:
                            st.write(f"**AI Priority:** {ticket.qualified_priority} ({ticket.qualified_by})")
                        st.write(f"**Created:** {datetime.fromtimestamp(ticket.created_at).strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        st.write(f"**Description:** {ticket.description}")
                        if ticket.lat and ticket.lon:
                            st.write(f"**Location:** ({ticket.lat:.6f}, {ticket.lon:.6f})")
                        if ticket.report_id:
                            st.write(f"**Linked Report:** {ticket.report_id}")
                    
                    # Update status
                    new_status = st.selectbox(
                        f"Update Status for {ticket.id}",
                        ["open", "in_progress", "closed"],
                        index=["open", "in_progress", "closed"].index(ticket.status),
                        key=f"status_{ticket.id}"
                    )
                    if new_status != ticket.status:
                        if st.button(f"Update {ticket.id}", key=f"update_{ticket.id}"):
                            ticket.status = new_status
                            st.session_state.tickets[ticket.id] = ticket
                            st.success(f"Status updated to {new_status}")
                            st.rerun()
        else:
            st.info("No tickets created yet")

elif page == "Map View":
    st.title("🗺️ Interactive Map")
    
    # Use the interactive map to show all reports and resources
    st.write("**Interactive map showing all reports (🔴) and resources (🟢)**")
    clicked_lat, clicked_lon, map_data = create_interactive_map(key="view_map")
    
    if clicked_lat and clicked_lon:
        st.info(f"📍 You clicked at coordinates: ({clicked_lat:.6f}, {clicked_lon:.6f})")
    
    # Legend
    st.subheader("Map Legend")
    col1, col2 = st.columns(2)
    with col1:
        st.write("🔴 **Reports** - Disaster incidents")
        if st.session_state.reports:
            for report in st.session_state.reports.values():
                st.write(f"  • {report.id}: {report.category} (urgency: {report.urgency})")
        else:
            st.write("  • No reports yet")
    with col2:
        st.write("🟢 **Resources** - Available help")
        if st.session_state.resources:
            for resource in st.session_state.resources.values():
                st.write(f"  • {resource.name}: {resource.type} (capacity: {resource.capacity})")
        else:
            st.write("  • No resources yet")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**UnityAid** - Disaster Response Coordination")
st.sidebar.markdown("Streamlit Version")

# Auto-refresh option
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()