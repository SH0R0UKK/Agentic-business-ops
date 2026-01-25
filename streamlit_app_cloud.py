"""
Streamlit Cloud Deployment - All-in-One App
Runs both backend API and frontend UI in a single deployment
"""

import streamlit as st
import requests
import json
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
import threading

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Page config
st.set_page_config(
    page_title="Business Ops AI Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Start backend API in background
@st.cache_resource
def start_backend():
    """Start FastAPI backend in background thread"""
    def run_api():
        import uvicorn
        # Set environment variables
        os.environ['PERPLEXITY_API_KEY'] = st.secrets.get('PERPLEXITY_API_KEY', '')
        os.environ['LANGSMITH_API_KEY'] = st.secrets.get('LANGSMITH_API_KEY', '')
        
        # Import and run the API
        from backend.api import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
    thread = threading.Thread(target=run_api, daemon=True)
    thread.start()
    time.sleep(3)  # Give API time to start
    return "Backend started"

# Start backend
try:
    backend_status = start_backend()
    API_BASE = "http://localhost:8000"
except Exception as e:
    st.error(f"Failed to start backend: {e}")
    API_BASE = "http://localhost:8000"

# Import the main UI
from streamlit_professional_ui import *

# The rest of the app is handled by streamlit_professional_ui.py
