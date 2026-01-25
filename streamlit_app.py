"""
Streamlit UI for Agentic Business Ops Platform
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Agentic Business Ops",
    page_icon="🚀",
    layout="wide"
)

# API Base URL
API_BASE = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚀 Agentic Business Ops</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Business Consultancy for Egyptian Startups</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Agentic+Ops", width=300)
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This platform uses multi-agent AI to:
    - 📄 Extract business insights from documents
    - 🔍 Answer questions about your business
    - 📋 Generate actionable business plans
    """)
    st.markdown("---")
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("⚠️ API Issue")
    except:
        st.error("❌ API Offline")
        st.info("Start backend: `python -m uvicorn backend.api:app --port 8000`")

# Session state
if 'startup_id' not in st.session_state:
    st.session_state.startup_id = None

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "💬 Ask Question", "📋 Generate Plan", "📊 View Profile"])

# Tab 1: Upload Documents
with tab1:
    st.header("📤 Upload Business Documents")
    st.markdown("Upload your business plan, pitch deck, or any business document to get started.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'doc', 'docx'],
            help="Upload your business document (PDF, Word, or Text)"
        )
        
        startup_id_input = st.text_input(
            "Startup ID (optional)",
            placeholder="Leave empty to generate new ID",
            help="Provide an existing startup ID to update, or leave empty for new"
        )
    
    with col2:
        st.info("**Accepted formats:**\n- Text (.txt)\n- PDF (.pdf)\n- Word (.doc, .docx)")
    
    if st.button("🚀 Upload & Process", type="primary"):
        if uploaded_file:
            with st.spinner("Uploading and processing document..."):
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
                        
                        st.success(f"✅ {result['message']}")
                        st.markdown(f"**Startup ID:** `{result['startup_id']}`")
                        st.info("💡 You can now ask questions or generate a plan using this startup ID!")
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload a file first!")

# Tab 2: Ask Questions
with tab2:
    st.header("💬 Ask Questions About Your Business")
    st.markdown("Get AI-powered insights by asking questions about your business documents.")
    
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
            height=100
        )
    
    with col2:
        st.info("**Example questions:**\n- What is my target market?\n- What are my key challenges?\n- What is my revenue model?\n- Who are my competitors?")
    
    if st.button("🔍 Get Answer", type="primary"):
        if question_startup_id and question:
            with st.spinner("🤖 AI is thinking... (this may take 30-60 seconds)"):
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
                        st.markdown(f"<div class='success-box'>{result['answer']}</div>", unsafe_allow_html=True)
                        
                        if result.get('supporting_evidence'):
                            with st.expander("📚 Supporting Evidence"):
                                for idx, evidence in enumerate(result['supporting_evidence'], 1):
                                    st.markdown(f"**Source {idx}:** {evidence.get('source_type', 'N/A')}")
                                    st.markdown(evidence.get('summary', 'No summary'))
                                    st.markdown("---")
                    else:
                        st.error(f"Request failed: {response.text}")
                except requests.exceptions.Timeout:
                    st.warning("⏱️ Request timed out. The AI is still processing. Try again in a moment.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please provide both Startup ID and a question!")

# Tab 3: Generate Plan
with tab3:
    st.header("📋 Generate Business Action Plan")
    st.markdown("Create a detailed, time-bound action plan with tasks and milestones.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        plan_startup_id = st.text_input(
            "Startup ID",
            value=st.session_state.startup_id or "",
            key="plan_startup_id",
            help="Enter the startup ID from document upload"
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
            help="How many days should the plan cover?"
        )
    
    with col2:
        st.info(f"**Plan Duration:** {time_horizon} days\n\n**Example goals:**\n- Launch MVP\n- Acquire first customers\n- Secure funding\n- Enter new market")
    
    if st.button("🎯 Generate Plan", type="primary"):
        if plan_startup_id and goal:
            with st.spinner("🤖 AI is creating your plan... (this may take 60-120 seconds)"):
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
                        
                        st.success(f"✅ Plan created: {result['title']}")
                        
                        # Display plan details
                        st.markdown(f"**Plan ID:** `{result['plan_id']}`")
                        st.markdown(f"**Created:** {result['created_at'][:10]}")
                        
                        # Show phases
                        if result.get('phases'):
                            st.markdown("### 📊 Phases")
                            for phase in result['phases']:
                                with st.expander(f"Phase {phase['order']}: {phase['name']}"):
                                    st.markdown(f"**Duration:** {phase['start_date']} → {phase['end_date']}")
                        
                        # Show tasks
                        if result.get('tasks'):
                            st.markdown(f"### ✅ Tasks ({len(result['tasks'])})")
                            for task in result['tasks']:
                                col_task, col_status = st.columns([4, 1])
                                with col_task:
                                    st.markdown(f"**{task['title']}**")
                                    st.markdown(task.get('description', 'No description')[:200])
                                with col_status:
                                    st.markdown(f"Priority: {task['priority']}")
                                    st.markdown(f"Status: {task['status']}")
                                st.markdown("---")
                        
                        # Strategy advice
                        if result.get('strategy_advice'):
                            with st.expander("💡 Strategy Advice"):
                                st.markdown(result['strategy_advice'])
                                
                    else:
                        st.error(f"Request failed: {response.text}")
                except requests.exceptions.Timeout:
                    st.warning("⏱️ Request timed out. The AI is still working. Try again in a moment.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please provide both Startup ID and a goal!")

# Tab 4: View Profile
with tab4:
    st.header("📊 View Startup Profile")
    st.markdown("View the extracted business profile from your documents.")
    
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
                        
                        # Display profile in a nice format
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Business Information")
                            st.markdown(f"**Name:** {profile.get('business_name', 'N/A')}")
                            st.markdown(f"**Type:** {profile.get('business_type', 'N/A')}")
                            st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
                            st.markdown(f"**Stage:** {profile.get('stage', 'N/A')}")
                        
                        with col2:
                            st.markdown("### Additional Details")
                            st.markdown(f"**Sector:** {profile.get('sector', 'N/A')}")
                            st.markdown(f"**Founded:** {profile.get('founded', 'N/A')}")
                            st.markdown(f"**Target Audience:** {profile.get('target_audience', 'N/A')}")
                        
                        if profile.get('goals'):
                            st.markdown("### 🎯 Goals")
                            for goal in profile['goals']:
                                st.markdown(f"- {goal}")
                        
                        if profile.get('key_constraints'):
                            st.markdown("### ⚠️ Key Constraints")
                            for constraint in profile['key_constraints']:
                                st.markdown(f"- {constraint}")
                        
                        if profile.get('competitors'):
                            st.markdown("### 🏢 Competitors")
                            for competitor in profile['competitors']:
                                st.markdown(f"- {competitor}")
                        
                        # Show raw JSON in expander
                        with st.expander("📄 View Raw Data"):
                            st.json(profile)
                            
                    elif response.status_code == 404:
                        st.warning("Profile not found. Please upload documents first.")
                    else:
                        st.error(f"Request failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a Startup ID!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Powered by LangGraph, Perplexity AI & FastAPI</p>
    <p>🚀 Agentic Business Ops Platform | Built for Egyptian Startups</p>
</div>
""", unsafe_allow_html=True)
