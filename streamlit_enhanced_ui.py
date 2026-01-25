"""
Enhanced Professional Streamlit UI for Agentic Business Ops
Replicates the Next.js frontend features with modern design
Run with: streamlit run streamlit_enhanced_ui.py
"""

import streamlit as st
import requests
import json
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Agentic Business Ops - AI Co-pilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE = "http://localhost:8000"

# Enhanced Custom CSS for professional look
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-purple: #8b5cf6;
        --primary-pink: #ec4899;
        --danger-red: #ef4444;
        --success-green: #10b981;
        --info-blue: #3b82f6;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .kpi-card-critical {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 4px solid #ef4444;
    }
    
    .kpi-card-success {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #10b981;
    }
    
    .kpi-card-info {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #3b82f6;
    }
    
    .kpi-card-purple {
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        border-left: 4px solid #8b5cf6;
    }
    
    .kpi-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-subtitle {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    
    /* Badge styles */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-critical {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .badge-high {
        background-color: #fed7aa;
        color: #9a3412;
    }
    
    .badge-medium {
        background-color: #fef9c3;
        color: #854d0e;
    }
    
    .badge-low {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .badge-success {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .badge-info {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .badge-purple {
        background-color: #f3e8ff;
        color: #6b21a8;
    }
    
    /* Status indicator */
    .status-active {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        color: #8b5cf6;
    }
    
    /* Activity timeline */
    .activity-item {
        padding: 0.75rem;
        border-left: 2px solid #e2e8f0;
        margin-bottom: 0.5rem;
        position: relative;
    }
    
    .activity-item::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 1rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #3b82f6;
    }
    
    .activity-time {
        font-size: 0.75rem;
        color: #94a3b8;
    }
    
    /* Profile section */
    .profile-section {
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9d5ff;
        margin-bottom: 1rem;
    }
    
    .profile-field {
        margin-bottom: 1rem;
    }
    
    .profile-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    
    .profile-value {
        font-size: 0.9375rem;
        color: #1e293b;
        font-weight: 500;
    }
    
    /* Gap analysis card */
    .gap-card {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.75rem;
        background-color: white;
    }
    
    .gap-card-critical {
        border-left: 4px solid #ef4444;
        background-color: #fef2f2;
    }
    
    .gap-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 0.5rem;
    }
    
    .gap-title {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.9375rem;
    }
    
    .confidence-score {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6366f1;
    }
    
    /* Success message */
    .success-message {
        padding: 1rem;
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-message {
        padding: 1rem;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Task card */
    .task-card {
        padding: 1rem;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        background-color: white;
        transition: box-shadow 0.2s;
    }
    
    .task-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .task-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .task-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'startup_id' not in st.session_state:
    st.session_state.startup_id = None
if 'current_profile' not in st.session_state:
    st.session_state.current_profile = None

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🚀 Agentic Business Ops")
    st.markdown("---")
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=3)
        if response.status_code == 200:
            st.markdown('<div class="status-active">✨ AI Co-pilot Active</div>', unsafe_allow_html=True)
        else:
            st.error("⚠️ API Issue")
    except:
        st.error("❌ API Offline")
        st.info("Start: `python -m uvicorn backend.api:app --port 8000`")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📤 Upload Documents", "🔍 Ask Questions", "📋 Generate Plan", "👤 View Profile", "⚠️ Gap Analysis"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    if st.session_state.startup_id:
        st.markdown("#### Current Session")
        st.markdown(f"**ID:** `{st.session_state.startup_id[:8]}...`")
    
    st.markdown("---")
    st.markdown("##### About")
    st.markdown("""
    Multi-agent AI system for:
    - 📄 Document analysis
    - 🔍 Business insights
    - 📋 Action planning
    - ⚠️ Gap identification
    """)

# Header
st.markdown('<div class="main-header">🚀 Agentic Business Ops</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Business Consultancy for Egyptian Startups</div>', unsafe_allow_html=True)

# Page routing
if page == "🏠 Dashboard":
    st.markdown("## 📊 Dashboard Overview")
    
    # Welcome message
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Welcome back!")
        st.markdown("Here's what's happening with your business today.")
    with col2:
        st.markdown('<div class="status-active">✨ AI Co-pilot Active</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card kpi-card-critical">
            <div class="kpi-label">⚠️ Critical Gaps</div>
            <div class="kpi-number" style="color: #ef4444;">3</div>
            <div class="kpi-subtitle">Requires immediate attention</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="kpi-card kpi-card-purple">
            <div class="kpi-label">📅 Upcoming Events</div>
            <div class="kpi-number" style="color: #8b5cf6;">5</div>
            <div class="kpi-subtitle">Scheduled this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="kpi-card kpi-card-info">
            <div class="kpi-label">🎯 Goals Tracked</div>
            <div class="kpi-number" style="color: #3b82f6;">4</div>
            <div class="kpi-subtitle">On track for completion</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="kpi-card kpi-card-success">
            <div class="kpi-label">📄 Documents</div>
            <div class="kpi-number" style="color: #10b981;">5</div>
            <div class="kpi-subtitle">Analyzed and indexed</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📤 Upload Document", use_container_width=True):
            st.session_state.page = "📤 Upload Documents"
            st.rerun()
    
    with col2:
        if st.button("🔍 Ask Question", use_container_width=True):
            st.session_state.page = "🔍 Ask Questions"
            st.rerun()
    
    with col3:
        if st.button("📋 Generate Plan", use_container_width=True):
            st.session_state.page = "📋 Generate Plan"
            st.rerun()
    
    with col4:
        if st.button("⚠️ View Gaps", use_container_width=True):
            st.session_state.page = "⚠️ Gap Analysis"
            st.rerun()
    
    st.markdown("---")
    
    # Recent Activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Recent Activity")
        st.markdown("""
        <div class="activity-item">
            <strong>New gap identified</strong><br>
            <span style="color: #64748b;">Inventory sync issue</span><br>
            <span class="activity-time">2 hours ago</span>
        </div>
        <div class="activity-item">
            <strong>Document analyzed</strong><br>
            <span style="color: #64748b;">Business plan uploaded</span><br>
            <span class="activity-time">4 hours ago</span>
        </div>
        <div class="activity-item">
            <strong>Plan generated</strong><br>
            <span style="color: #64748b;">Q2 Marketing Strategy</span><br>
            <span class="activity-time">1 day ago</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Active Goals")
        st.markdown('<span class="badge badge-purple">Marketing</span>', unsafe_allow_html=True)
        st.markdown("Increase online sales by 40%")
        st.progress(0.65)
        
        st.markdown("")
        st.markdown('<span class="badge badge-info">Operations</span>', unsafe_allow_html=True)
        st.markdown("Launch subscription service")
        st.progress(0.30)
        
        st.markdown("")
        st.markdown('<span class="badge badge-success">Growth</span>', unsafe_allow_html=True)
        st.markdown("Acquire 10 B2B clients")
        st.progress(0.80)

elif page == "📤 Upload Documents":
    st.markdown("## 📤 Upload Business Documents")
    st.markdown("Upload your business plan, pitch deck, or any document to extract insights and create your business profile.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'doc', 'docx'],
            help="Upload your business document"
        )
        
        startup_id_input = st.text_input(
            "Startup ID (optional)",
            placeholder="Leave empty to generate new ID",
            help="Provide existing ID to update, or leave empty"
        )
        
        if st.button("🚀 Upload & Process", type="primary"):
            if uploaded_file:
                with st.spinner("⏳ Processing document... This may take 10-30 seconds"):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        data = {}
                        if startup_id_input:
                            data["startup_id"] = startup_id_input
                        
                        response = requests.post(
                            f"{API_BASE}/api/upload",
                            files=files,
                            data=data,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.startup_id = result["startup_id"]
                            
                            st.markdown(f"""
                            <div class="success-message">
                                <strong>✅ {result['message']}</strong><br>
                                <strong>Startup ID:</strong> <code>{result['startup_id']}</code>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("""
                            <div class="info-message">
                                💡 <strong>Next Steps:</strong> You can now ask questions or generate a plan using this startup ID!
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Upload failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a file first!")
    
    with col2:
        st.markdown("""
        <div class="info-message">
            <strong>📄 Accepted Formats:</strong><br>
            • Text (.txt)<br>
            • PDF (.pdf)<br>
            • Word (.doc, .docx)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-message">
            <strong>💡 What we extract:</strong><br>
            • Business name & type<br>
            • Goals & objectives<br>
            • Target audience<br>
            • Key constraints<br>
            • Competitors
        </div>
        """, unsafe_allow_html=True)

elif page == "🔍 Ask Questions":
    st.markdown("## 💬 Ask Questions About Your Business")
    st.markdown("Get AI-powered insights by asking questions about your uploaded documents and business context.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question_startup_id = st.text_input(
            "Startup ID",
            value=st.session_state.startup_id or "",
            key="question_startup_id",
            help="Enter the startup ID from document upload"
        )
        
        question = st.text_area(
            "Your Question",
            placeholder="e.g., What is my target market? What are the key challenges? What is my competitive advantage?",
            height=120
        )
        
        if st.button("🔍 Get Answer", type="primary"):
            if question_startup_id and question:
                with st.spinner("🤖 AI is analyzing... (30-60 seconds)"):
                    try:
                        payload = {
                            "startup_id": question_startup_id,
                            "question": question
                        }
                        
                        response = requests.post(
                            f"{API_BASE}/api/question",
                            json=payload,
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.markdown("### 📝 Answer")
                            st.markdown(f"""
                            <div class="success-message">
                                {result['answer']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if result.get('supporting_evidence'):
                                with st.expander("📚 Supporting Evidence"):
                                    for idx, evidence in enumerate(result['supporting_evidence'], 1):
                                        st.markdown(f"**Source {idx}:** {evidence.get('source_type', 'N/A')}")
                                        st.markdown(evidence.get('summary', 'No summary'))
                                        st.markdown("---")
                        else:
                            st.error(f"Request failed: {response.text}")
                    except requests.exceptions.Timeout:
                        st.warning("⏱️ Request timed out. Try again in a moment.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("⚠️ Please provide both Startup ID and question!")
    
    with col2:
        st.markdown("""
        <div class="info-message">
            <strong>💡 Example Questions:</strong><br>
            • What is my target market?<br>
            • What are my key challenges?<br>
            • What is my revenue model?<br>
            • Who are my competitors?<br>
            • What is my unique value?
        </div>
        """, unsafe_allow_html=True)

elif page == "📋 Generate Plan":
    st.markdown("## 📋 Generate Business Action Plan")
    st.markdown("Create a detailed, time-bound action plan with tasks, phases, and milestones.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        plan_startup_id = st.text_input(
            "Startup ID",
            value=st.session_state.startup_id or "",
            key="plan_startup_id"
        )
        
        goal = st.text_area(
            "Business Goal",
            placeholder="e.g., Launch MVP and acquire first 100 users",
            height=100
        )
        
        time_horizon = st.slider(
            "Time Horizon (days)",
            min_value=7,
            max_value=180,
            value=60,
            help="Duration for the plan"
        )
        
        if st.button("🎯 Generate Plan", type="primary"):
            if plan_startup_id and goal:
                with st.spinner("🤖 AI is creating your strategic plan... (60-120 seconds)"):
                    try:
                        payload = {
                            "startup_id": plan_startup_id,
                            "goal": goal,
                            "time_horizon_days": time_horizon
                        }
                        
                        response = requests.post(
                            f"{API_BASE}/api/plan",
                            json=payload,
                            timeout=180
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.markdown(f"""
                            <div class="success-message">
                                <strong>✅ Plan Created: {result['title']}</strong><br>
                                Plan ID: <code>{result['plan_id']}</code><br>
                                Created: {result['created_at'][:10]}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show phases
                            if result.get('phases'):
                                st.markdown("### 📊 Plan Phases")
                                for phase in result['phases']:
                                    with st.expander(f"📌 Phase {phase['order']}: {phase['name']}"):
                                        st.markdown(f"**Duration:** {phase['start_date']} → {phase['end_date']}")
                            
                            # Show tasks
                            if result.get('tasks'):
                                st.markdown(f"### ✅ Tasks ({len(result['tasks'])})")
                                for task in result['tasks']:
                                    priority_badge = {
                                        'high': 'badge-critical',
                                        'medium': 'badge-medium',
                                        'low': 'badge-low'
                                    }.get(task['priority'], 'badge-info')
                                    
                                    st.markdown(f"""
                                    <div class="task-card">
                                        <div class="task-title">{task['title']}</div>
                                        <div>{task.get('description', 'No description')[:200]}</div>
                                        <div class="task-meta">
                                            <span class="badge {priority_badge}">{task['priority'].upper()}</span>
                                            <span>Status: {task['status']}</span>
                                            <span>📅 {task['start_date']} → {task['end_date']}</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Strategy advice
                            if result.get('strategy_advice'):
                                with st.expander("💡 Strategic Advice"):
                                    st.markdown(result['strategy_advice'])
                                    
                        else:
                            st.error(f"Request failed: {response.text}")
                    except requests.exceptions.Timeout:
                        st.warning("⏱️ Request timed out. Try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("⚠️ Provide Startup ID and goal!")
    
    with col2:
        st.markdown(f"""
        <div class="info-message">
            <strong>📅 Plan Duration:</strong><br>
            {time_horizon} days
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-message">
            <strong>💡 Example Goals:</strong><br>
            • Launch MVP<br>
            • Acquire first customers<br>
            • Secure seed funding<br>
            • Enter new market
        </div>
        """, unsafe_allow_html=True)

elif page == "👤 View Profile":
    st.markdown("## 📊 Business Profile")
    st.markdown("View your extracted business information and insights.")
    
    profile_startup_id = st.text_input(
        "Startup ID",
        value=st.session_state.startup_id or "",
        key="profile_startup_id"
    )
    
    if st.button("🔍 Load Profile", type="primary"):
        if profile_startup_id:
            with st.spinner("Loading profile..."):
                try:
                    response = requests.get(
                        f"{API_BASE}/api/profile/{profile_startup_id}",
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        profile = response.json()
                        st.session_state.current_profile = profile
                        
                        # Display profile
                        st.markdown("""
                        <div class="profile-section">
                            <h3>🏢 Business Overview</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Business Name:** {profile.get('business_name', 'N/A')}")
                            st.markdown(f"**Type:** {profile.get('business_type', 'N/A')}")
                            st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Stage:** {profile.get('stage', 'N/A')}")
                            st.markdown(f"**Sector:** {profile.get('sector', 'N/A')}")
                            st.markdown(f"**Founded:** {profile.get('founded', 'N/A')}")
                        
                        st.markdown("---")
                        
                        if profile.get('goals'):
                            st.markdown("### 🎯 Business Goals")
                            for goal in profile['goals']:
                                st.markdown(f'<span class="badge badge-purple">Goal</span> {goal}', unsafe_allow_html=True)
                        
                        if profile.get('key_constraints'):
                            st.markdown("### ⚠️ Key Constraints")
                            for constraint in profile['key_constraints']:
                                st.markdown(f'<span class="badge badge-critical">Constraint</span> {constraint}', unsafe_allow_html=True)
                        
                        if profile.get('target_audience'):
                            st.markdown("### 👥 Target Audience")
                            st.info(profile['target_audience'])
                        
                        if profile.get('competitors'):
                            st.markdown("### 🏢 Competitors")
                            for competitor in profile['competitors']:
                                st.markdown(f"• {competitor}")
                        
                        # Raw JSON
                        with st.expander("📄 View Raw Data"):
                            st.json(profile)
                            
                    elif response.status_code == 404:
                        st.warning("⚠️ Profile not found. Upload documents first.")
                    else:
                        st.error(f"Request failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Enter a Startup ID!")

elif page == "⚠️ Gap Analysis":
    st.markdown("## ⚠️ Gap Analysis")
    st.markdown("Identify internal gaps and market opportunities to improve your business strategy.")
    
    st.markdown("""
    <div class="info-message">
        <strong>💡 What is Gap Analysis?</strong><br>
        Our AI identifies internal operational gaps and external market opportunities by analyzing your business profile against industry best practices and competitor benchmarks.
    </div>
    """, unsafe_allow_html=True)
    
    # Mock gaps data (would come from API in real implementation)
    st.markdown("### 🔴 Critical Gaps (Immediate Attention Required)")
    
    st.markdown("""
    <div class="gap-card gap-card-critical">
        <div class="gap-header">
            <div class="gap-title">⚠️ Inventory tracking system lacks real-time sync</div>
            <span class="badge badge-critical">CRITICAL</span>
        </div>
        <div style="margin-top: 0.5rem; color: #64748b; font-size: 0.875rem;">
            Current system updates every 4 hours, causing overselling during peak traffic. 
            Real-time webhooks would resolve this within 2-3 sprint cycles.
        </div>
        <div style="margin-top: 0.5rem;">
            <span class="badge badge-info">Internal</span>
            <span style="margin-left: 0.5rem; font-size: 0.75rem; color: #64748b;">
                Confidence: 92% | 🚫 Goal Blocking
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="gap-card gap-card-critical">
        <div class="gap-header">
            <div class="gap-title">⚠️ Competitors offering same-day delivery</div>
            <span class="badge badge-critical">HIGH THREAT</span>
        </div>
        <div style="margin-top: 0.5rem; color: #64748b; font-size: 0.875rem;">
            Three major competitors now offer same-day delivery in top metros. 
            Our 3-5 day shipping is becoming a competitive disadvantage.
        </div>
        <div style="margin-top: 0.5rem;">
            <span class="badge badge-high">Market</span>
            <span style="margin-left: 0.5rem; font-size: 0.75rem; color: #64748b;">
                Confidence: 88% | 🚫 Goal Blocking
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🟡 Medium Priority Gaps")
    
    st.markdown("""
    <div class="gap-card">
        <div class="gap-header">
            <div class="gap-title">Marketing automation lacks personalization</div>
            <span class="badge badge-medium">MEDIUM</span>
        </div>
        <div style="margin-top: 0.5rem; color: #64748b; font-size: 0.875rem;">
            Current email campaigns use basic segmentation. Behavioral triggers could increase conversions by 25%.
        </div>
        <div style="margin-top: 0.5rem;">
            <span class="badge badge-info">Internal</span>
            <span style="margin-left: 0.5rem; font-size: 0.75rem; color: #64748b;">
                Confidence: 78%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="task-card">
            <div class="task-title">🎯 Quick Wins</div>
            <div style="margin-top: 0.5rem;">
                • Implement real-time inventory sync<br>
                • Partner with local fulfillment centers<br>
                • Automate customer service routing
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="task-card">
            <div class="task-title">📅 Long-term Initiatives</div>
            <div style="margin-top: 0.5rem;">
                • Build predictive analytics system<br>
                • Develop personalization engine<br>
                • Expand same-day delivery network
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 2rem; font-size: 0.875rem;'>
    <p style='margin-bottom: 0.5rem;'>Powered by LangGraph, Perplexity AI & FastAPI</p>
    <p style='margin: 0;'>🚀 Agentic Business Ops Platform | Built for Egyptian Startups</p>
</div>
""", unsafe_allow_html=True)
