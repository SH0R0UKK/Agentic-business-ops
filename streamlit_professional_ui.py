"""
Professional Streamlit UI for Agentic Business Ops
Modern, clean design with authentication and fast navigation
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Only set page config if not already set (when run standalone)
if 'page_config_set' not in st.session_state:
    st.set_page_config(
        page_title="Business Ops AI Platform",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.session_state.page_config_set = True

# API Base URL - use environment variable for production, fallback to localhost
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Professional CSS - Clean, light theme with excellent contrast
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Root variables */
    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --success: #059669;
        --danger: #dc2626;
        --warning: #d97706;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-700: #374151;
        --gray-900: #111827;
    }
    
    /* Main container */
    .main {
        background-color: #ffffff;
        padding: 2rem 4rem;
    }
    
    /* Professional header */
    .app-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 1.5rem 2rem;
        margin: -2rem -4rem 2rem -4rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .app-subtitle {
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
        color: rgba(255,255,255,0.9);
    }
    
    /* Navigation tabs */
    .nav-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid var(--gray-200);
        padding-bottom: 0;
    }
    
    .nav-tab {
        padding: 0.75rem 1.5rem;
        background: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        color: var(--gray-700);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .nav-tab:hover {
        color: var(--primary);
        border-bottom-color: var(--gray-300);
    }
    
    .nav-tab-active {
        color: var(--primary);
        border-bottom-color: var(--primary);
    }
    
    /* Cards */
    .card {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .card-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--gray-200);
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s;
    }
    
    .stat-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gray-900);
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--gray-700);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-change {
        font-size: 0.75rem;
        color: var(--success);
        margin-top: 0.25rem;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .badge-danger {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .badge-warning {
        background-color: #fed7aa;
        color: #9a3412;
    }
    
    .badge-info {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .badge-primary {
        background-color: #e0e7ff;
        color: #3730a3;
    }
    
    /* Alert boxes */
    .alert {
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .alert-success {
        background-color: #d1fae5;
        border-color: #059669;
        color: #065f46;
    }
    
    .alert-info {
        background-color: #dbeafe;
        border-color: #2563eb;
        color: #1e40af;
    }
    
    .alert-warning {
        background-color: #fef3c7;
        border-color: #d97706;
        color: #92400e;
    }
    
    .alert-danger {
        background-color: #fee2e2;
        border-color: #dc2626;
        color: #991b1b;
    }
    
    /* Login page */
    .login-container {
        max-width: 420px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }
    
    .login-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--gray-900);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        font-size: 0.875rem;
        color: var(--gray-700);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Task list */
    .task-item {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: border-color 0.2s;
    }
    
    .task-item:hover {
        border-color: var(--primary);
    }
    
    .task-title {
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: 0.25rem;
    }
    
    .task-meta {
        font-size: 0.75rem;
        color: var(--gray-700);
    }
    
    /* Timeline */
    .timeline-item {
        padding-left: 2rem;
        position: relative;
        padding-bottom: 1.5rem;
        border-left: 2px solid var(--gray-200);
        margin-left: 0.5rem;
    }
    
    .timeline-item:last-child {
        border-left-color: transparent;
    }
    
    .timeline-dot {
        position: absolute;
        left: -6px;
        top: 0;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: var(--primary);
    }
    
    .timeline-time {
        font-size: 0.75rem;
        color: var(--gray-700);
        margin-bottom: 0.25rem;
    }
    
    .timeline-content {
        font-size: 0.875rem;
        color: var(--gray-900);
        font-weight: 500;
    }
    
    /* Message bubble */
    .message-bubble {
        background: var(--gray-50);
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .message-bubble-ai {
        background: #eff6ff;
        border-color: #bfdbfe;
    }
    
    .message-header {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--gray-700);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .message-content {
        color: var(--gray-900);
        line-height: 1.6;
    }
    
    /* Button override */
    .stButton button {
        background-color: var(--primary);
        color: white;
        border: none;
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        border-radius: 6px;
        transition: background-color 0.2s;
    }
    
    .stButton button:hover {
        background-color: var(--primary-dark);
    }
    
    /* Input styling */
    .stTextInput input, .stTextArea textarea {
        border: 1px solid var(--gray-300);
        border-radius: 6px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Remove padding from main for cleaner look */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'startup_id' not in st.session_state:
    st.session_state.startup_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'chat'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_uploaded' not in st.session_state:
    st.session_state.documents_uploaded = 0
if 'plans_generated' not in st.session_state:
    st.session_state.plans_generated = 0
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
if 'tasks_completed' not in st.session_state:
    st.session_state.tasks_completed = 0
if 'current_tasks' not in st.session_state:
    st.session_state.current_tasks = []
if 'work_hours' not in st.session_state:
    st.session_state.work_hours = None

# Login/Signup Page
def show_auth_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-title">Business Ops AI Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">AI-powered business consultancy for growth</p>', unsafe_allow_html=True)
    
    auth_tab = st.radio("Authentication Mode", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
    
    if auth_tab == "Login":
        email = st.text_input("Email Address", placeholder="your.email@company.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Sign In", use_container_width=True):
            if email and password:
                # Authentication
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please enter email and password")
    
    else:  # Sign Up
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="John")
        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")
        
        email = st.text_input("Work Email", placeholder="your.email@company.com")
        company = st.text_input("Company Name", placeholder="Your Company")
        password = st.text_input("Create Password", type="password", placeholder="Min. 8 characters")
        
        if st.button("Create Account", use_container_width=True):
            if email and password and first_name and company:
                # Registration
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please fill all required fields")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem; color: #6b7280; font-size: 0.875rem;'>
        <p>Trusted by Egyptian startups | Powered by Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)

# Main Application
def show_main_app():
    # Header
    st.markdown(f"""
    <div class="app-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="app-title">Business Ops AI Platform</h1>
                <p class="app-subtitle">Welcome back, {st.session_state.user_email.split('@')[0].title()}</p>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span class="badge badge-success">AI Active</span>
                <button onclick="window.location.reload()" style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Sign Out</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3, col4 = st.columns([2, 2, 2, 6])
    
    with col1:
        if st.button("Chat & Upload", use_container_width=True, type="primary" if st.session_state.current_page == 'chat' else "secondary"):
            st.session_state.current_page = 'chat'
    
    with col2:
        if st.button("Plans & Calendar", use_container_width=True, type="primary" if st.session_state.current_page == 'plans' else "secondary"):
            st.session_state.current_page = 'plans'
    
    with col3:
        if st.button("Analytics", use_container_width=True, type="primary" if st.session_state.current_page == 'analytics' else "secondary"):
            st.session_state.current_page = 'analytics'
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Page content
    if st.session_state.current_page == 'chat':
        show_chat_page()
    elif st.session_state.current_page == 'plans':
        show_plans_page()
    elif st.session_state.current_page == 'analytics':
        show_analytics_page()

# Chat & Upload Page
def show_chat_page():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">AI Assistant</div>', unsafe_allow_html=True)
        
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="message-bubble">
                    <div class="message-header">You</div>
                    <div class="message-content">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-bubble message-bubble-ai">
                    <div class="message-header">AI Assistant</div>
                    <div class="message-content">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            question = st.text_area("Ask a question about your business", placeholder="e.g., What is my target market? What are my key challenges?", height=100, label_visibility="collapsed")
            submitted = st.form_submit_button("Send Message", use_container_width=True)
            
            if submitted and question and st.session_state.startup_id:
                st.session_state.chat_history.append({"role": "user", "content": question})
                st.session_state.questions_asked += 1
                
                with st.spinner("AI is analyzing..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/api/question",
                            json={"startup_id": st.session_state.startup_id, "question": question},
                            timeout=120
                        )
                        if response.status_code == 200:
                            answer = response.json()['answer']
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})
                            st.rerun()
                    except:
                        st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I encountered an error. Please try again."})
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Upload documents
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Upload Documents</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload business document", type=['txt', 'pdf', 'doc', 'docx'], label_visibility="collapsed")
        
        if uploaded_file:
            if st.button("Process Document", use_container_width=True):
                with st.spinner("Processing..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=60)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.startup_id = result["startup_id"]
                            st.session_state.documents_uploaded += 1
                            st.markdown(f"""
                            <div class="alert alert-success">
                                <strong>Success!</strong><br>
                                Document processed successfully
                            </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.startup_id:
            st.markdown(f"""
            <div class="alert alert-info">
                <strong>Active Session</strong><br>
                ID: {st.session_state.startup_id[:12]}...
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick tips
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Quick Tips</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.875rem; color: #374151;">
            <p><strong>Ask about:</strong></p>
            <ul style="margin: 0; padding-left: 1.25rem;">
                <li>Target market analysis</li>
                <li>Competitive positioning</li>
                <li>Growth opportunities</li>
                <li>Revenue strategies</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Plans & Calendar Page
def show_plans_page():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Work Hours Setup
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Work Schedule</div>', unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 0.875rem; color: #374151; margin-bottom: 1rem;'>When would you like to dedicate time to your business?</p>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            start_hour = st.selectbox("Start Time", [f"{h:02d}:00" for h in range(24)], index=9)
        with col_b:
            end_hour = st.selectbox("End Time", [f"{h:02d}:00" for h in range(24)], index=17)
        
        if st.button("Set Work Hours", use_container_width=True):
            st.session_state.work_hours = {"start": start_hour, "end": end_hour}
            st.success(f"Work hours set: {start_hour} - {end_hour}")
        
        if st.session_state.work_hours:
            st.markdown(f"""
            <div class="alert alert-info">
                <strong>Active Schedule:</strong> {st.session_state.work_hours['start']} - {st.session_state.work_hours['end']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate Plan
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Generate Action Plan</div>', unsafe_allow_html=True)
        
        goal = st.text_area("Business Goal", placeholder="e.g., Launch MVP and acquire first 100 users", height=100)
        time_horizon = st.slider("Time Horizon (days)", 7, 180, 60)
        
        if st.button("Generate Plan", use_container_width=True):
            if st.session_state.startup_id and goal:
                with st.spinner("Creating strategic plan..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/api/plan",
                            json={"startup_id": st.session_state.startup_id, "goal": goal, "time_horizon_days": time_horizon},
                            timeout=180
                        )
                        if response.status_code == 200:
                            plan = response.json()
                            st.session_state.plans_generated += 1
                            
                            st.markdown(f"""
                            <div class="alert alert-success">
                                <strong>Plan Created!</strong><br>
                                {plan['title']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add tasks to session state with proper priority distribution
                            if plan.get('tasks'):
                                st.session_state.current_tasks = []
                                for idx, task in enumerate(plan['tasks']):
                                    # Assign varied priorities
                                    if idx % 3 == 0:
                                        priority = 'high'
                                    elif idx % 3 == 1:
                                        priority = 'medium'
                                    else:
                                        priority = 'low'
                                    
                                    task_with_status = {
                                        'id': f"task_{idx}",
                                        'title': task.get('title', 'Untitled Task'),
                                        'priority': priority,
                                        'start_date': task.get('start_date', 'TBD'),
                                        'end_date': task.get('end_date', 'TBD'),
                                        'completed': False
                                    }
                                    st.session_state.current_tasks.append(task_with_status)
                                
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please upload a document first and enter a goal")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Task List with Checkboxes
        if st.session_state.current_tasks:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">Task List</div>', unsafe_allow_html=True)
            
            for task in st.session_state.current_tasks:
                col_check, col_task = st.columns([0.5, 9.5])
                
                with col_check:
                    completed = st.checkbox("", value=task['completed'], key=task['id'], label_visibility="collapsed")
                    if completed != task['completed']:
                        task['completed'] = completed
                        if completed:
                            st.session_state.tasks_completed += 1
                        else:
                            st.session_state.tasks_completed -= 1
                
                with col_task:
                    badge_class = {'high': 'danger', 'medium': 'warning', 'low': 'info'}.get(task['priority'], 'primary')
                    style = "text-decoration: line-through; opacity: 0.6;" if task['completed'] else ""
                    st.markdown(f"""
                    <div class="task-item" style="{style}">
                        <div>
                            <div class="task-title">{task['title']}</div>
                            <div class="task-meta">
                                <span class="badge badge-{badge_class}">{task['priority'].upper()}</span>
                                <span style="margin-left: 0.5rem;">{task['start_date']} - {task['end_date']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">Recent Activity</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-time">2 hours ago</div>
            <div class="timeline-content">Document uploaded</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-time">1 day ago</div>
            <div class="timeline-content">Plan generated</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-time">2 days ago</div>
            <div class="timeline-content">Account created</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Analytics Page
def show_analytics_page():
    st.markdown('<div class="card-header">Business Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Stats cards with user-specific data
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(st.session_state.current_tasks)
    completion_rate = int((st.session_state.tasks_completed / total_tasks * 100)) if total_tasks > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Documents</div>
            <div class="stat-number">{st.session_state.documents_uploaded}</div>
            <div class="stat-change">Total uploaded</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Active Plans</div>
            <div class="stat-number">{st.session_state.plans_generated}</div>
            <div class="stat-change">{total_tasks} tasks created</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Questions Asked</div>
            <div class="stat-number">{st.session_state.questions_asked}</div>
            <div class="stat-change">AI interactions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Tasks Completed</div>
            <div class="stat-number">{st.session_state.tasks_completed}</div>
            <div class="stat-change">{completion_rate}% completion</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Business profile
    if st.session_state.startup_id:
        with st.spinner("Loading profile..."):
            try:
                response = requests.get(f"{API_BASE}/api/profile/{st.session_state.startup_id}", timeout=30)
                if response.status_code == 200:
                    profile = response.json()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-header">Business Overview</div>', unsafe_allow_html=True)
                        st.markdown(f"**Name:** {profile.get('business_name', 'N/A')}")
                        st.markdown(f"**Type:** {profile.get('business_type', 'N/A')}")
                        st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
                        st.markdown(f"**Stage:** {profile.get('stage', 'N/A')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-header">Key Metrics</div>', unsafe_allow_html=True)
                        st.markdown(f"**Goals:** {len(profile.get('goals', []))}")
                        st.markdown(f"**Constraints:** {len(profile.get('key_constraints', []))}")
                        st.markdown(f"**Competitors:** {len(profile.get('competitors', []))}")
                        st.markdown('</div>', unsafe_allow_html=True)
            except:
                pass

# Main app logic
if not st.session_state.authenticated:
    show_auth_page()
else:
    show_main_app()
