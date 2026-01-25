"""
FastAPI Backend API for Agentic Business Ops Platform.
Provides endpoints for document upload, questions, and plan generation.

Run with: python backend/api.py
"""

import os
import sys
import uuid
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports to work
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import orchestrator and database utilities
from backend.agents.orchestrator.orchestrator import master_app
from backend.agents.state import MasterState
from backend.data.db.storage import (
    init_db,
    save_profile,
    get_profile,
    save_plan,
    get_plan,
    get_latest_plan,
    list_plans_for_startup,
)

# Initialize database
init_db()

# --- FASTAPI APP SETUP ---
app = FastAPI(
    title="Agentic Business Ops API",
    description="AI-powered business consultancy platform for Egyptian startups",
    version="1.0.0",
)

# CORS configuration for frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS ---

class QuestionRequest(BaseModel):
    startup_id: str
    question: str


class QuestionResponse(BaseModel):
    startup_id: str
    question: str
    answer: str
    supporting_evidence: List[Dict[str, Any]]


class PlanRequest(BaseModel):
    startup_id: str
    goal: str
    time_horizon_days: int = 60


class PlanPhase(BaseModel):
    phase_id: str
    name: str
    order: int
    start_date: str
    end_date: str


class PlanTask(BaseModel):
    task_id: str
    phase_id: str
    title: str
    description: str
    status: str = "todo"
    priority: str = "medium"
    assignee: Optional[str] = None
    start_date: str
    end_date: str
    dependencies: List[str] = []
    tags: List[str] = []


class PlanResponse(BaseModel):
    plan_id: str
    startup_id: str
    version: int
    title: str
    created_at: str
    time_horizon_days: int
    phases: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]


class UploadResponse(BaseModel):
    startup_id: str
    message: str


# --- PATHS ---
STARTUPS_DIR = Path(__file__).parent / "data" / "startups"
SOURCE_DIR = Path(__file__).parent.parent / "source"


# --- HELPER FUNCTIONS ---

def ensure_startup_dir(startup_id: str) -> Path:
    """Create and return the startup's data directory."""
    startup_dir = STARTUPS_DIR / startup_id
    startup_dir.mkdir(parents=True, exist_ok=True)
    return startup_dir


def run_orchestrator_question(startup_id: str, question: str) -> Dict[str, Any]:
    """
    Run the orchestrator to answer a question about a startup.
    Returns answer + supporting evidence.
    """
    # Load profile from database
    profile = get_profile(startup_id)
    if not profile:
        raise ValueError(f"Startup {startup_id} not found")
    
    # Get document files for this startup
    startup_dir = STARTUPS_DIR / startup_id
    source_files = []
    if startup_dir.exists():
        source_files = [str(f) for f in startup_dir.glob("*") if f.is_file()]
    
    # Build initial state
    initial_state: MasterState = {
        "messages": [HumanMessage(content=question)],
        "user_context": profile,
        "onboarding_status": "completed",  # Skip onboarding, profile already exists
        "onboarding_files": source_files,
        "processed_files": [],
        "next_agent": None,
        "action": None,
        "iteration_count": 0,
        "task_type": "advisory",
        "search_query": question,
        "final_plan": None,
        "research_data": None,
        "rag_data": None,
        "gap_analysis": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    # Run orchestrator
    final_state = None
    for step in master_app.stream(initial_state):
        node_name = list(step.keys())[0]
        logger.info(f"✅ Question flow - Step: {node_name}")
        final_state = step.get(node_name, {})
    
    # Extract answer and evidence
    answer = final_state.get("final_reply", "I couldn't find an answer to your question.")
    
    # Build supporting evidence from research results
    evidence = []
    
    if final_state.get("research_offline"):
        offline = final_state["research_offline"]
        if offline.get("summary"):
            evidence.append({
                "source_type": "offline",
                "summary": offline.get("summary", ""),
                "doc_title": "Internal Knowledge Base",
                "url": None,
            })
    
    if final_state.get("research_online"):
        online = final_state["research_online"]
        if online.get("summary"):
            evidence.append({
                "source_type": "online",
                "summary": online.get("summary", ""),
                "doc_title": "Web Research",
                "url": None,
            })
        # Add specific findings
        for finding in online.get("findings", [])[:3]:
            if isinstance(finding, dict):
                evidence.append({
                    "source_type": "online",
                    "summary": finding.get("pattern", str(finding)),
                    "doc_title": finding.get("source", "Web"),
                    "url": finding.get("url"),
                })
    
    return {
        "startup_id": startup_id,
        "question": question,
        "answer": answer,
        "supporting_evidence": evidence,
    }


def run_orchestrator_for_plan(startup_id: str, goal: str, time_horizon_days: int) -> Dict[str, Any]:
    """
    Run the full orchestrator pipeline to generate a business plan.
    Returns structured Plan JSON.
    """
    # Load or create profile
    profile = get_profile(startup_id)
    
    # Get document files
    startup_dir = STARTUPS_DIR / startup_id
    source_files = []
    if startup_dir.exists():
        source_files = [str(f) for f in startup_dir.glob("*") if f.is_file()]
    
    # Also check global source folder
    if SOURCE_DIR.exists():
        source_files.extend([str(f) for f in SOURCE_DIR.glob("*") if f.is_file()])
    
    # Build initial state with goal
    user_context = profile or {"business_name": "New Startup", "business_type": "Startup"}
    user_context["goals"] = goal
    
    initial_state: MasterState = {
        "messages": [HumanMessage(content=f"Create a {time_horizon_days}-day action plan for: {goal}")],
        "user_context": user_context,
        "onboarding_status": "completed" if profile else "pending",
        "onboarding_files": source_files if source_files else None,
        "processed_files": [],
        "next_agent": None,
        "action": None,
        "iteration_count": 0,
        "task_type": "timeline",
        "search_query": goal,
        "final_plan": None,
        "research_data": None,
        "rag_data": None,
        "gap_analysis": None,
        "research_offline": None,
        "research_online": None,
        "final_reply": None,
    }
    
    # Run full orchestrator pipeline
    final_state = {}
    for step in master_app.stream(initial_state):
        node_name = list(step.keys())[0]
        logger.info(f"✅ Plan flow - Step: {node_name}")
        # Merge state updates
        step_data = step.get(node_name, {})
        if isinstance(step_data, dict):
            final_state.update(step_data)
    
    # Extract or build plan from final state
    raw_plan = final_state.get("final_plan", {})
    
    # Generate plan ID and metadata
    plan_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    # Transform planner output to expected format
    plan_data = transform_plan_to_ui_format(
        raw_plan=raw_plan,
        plan_id=plan_id,
        startup_id=startup_id,
        goal=goal,
        time_horizon_days=time_horizon_days,
        created_at=now,
    )
    
    # Save plan to database
    save_plan(plan_data)
    
    return plan_data


def transform_plan_to_ui_format(
    raw_plan: Dict[str, Any],
    plan_id: str,
    startup_id: str,
    goal: str,
    time_horizon_days: int,
    created_at: str,
) -> Dict[str, Any]:
    """
    Transform the planner agent's output into the UI-expected format.
    """
    phases = []
    tasks = []
    
    # Extract schedule_events from planner output
    schedule_events = raw_plan.get("schedule_events", [])
    strategy_advice = raw_plan.get("strategy_advice", "")
    
    if schedule_events:
        # Group events into phases based on date proximity
        phase_id = "p1"
        phases.append({
            "phase_id": phase_id,
            "name": "Execution Phase",
            "order": 1,
            "start_date": schedule_events[0].get("date", created_at[:10]) if schedule_events else created_at[:10],
            "end_date": schedule_events[-1].get("date", created_at[:10]) if schedule_events else created_at[:10],
        })
        
        # Convert events to tasks
        for i, event in enumerate(schedule_events):
            task_id = f"t{i+1}"
            tasks.append({
                "task_id": task_id,
                "phase_id": phase_id,
                "title": event.get("task", f"Task {i+1}"),
                "description": event.get("details", ""),
                "status": "todo",
                "priority": "medium",
                "assignee": None,
                "start_date": event.get("date", created_at[:10]),
                "end_date": event.get("date", created_at[:10]),
                "dependencies": [],
                "tags": [],
            })
    else:
        # Create default phase if no events
        from datetime import timedelta
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=time_horizon_days)
        
        phases.append({
            "phase_id": "p1",
            "name": "Planning Phase",
            "order": 1,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        })
        
        # Create a task from the strategy advice
        if strategy_advice:
            tasks.append({
                "task_id": "t1",
                "phase_id": "p1",
                "title": "Review Strategy",
                "description": strategy_advice[:500] if len(strategy_advice) > 500 else strategy_advice,
                "status": "todo",
                "priority": "high",
                "assignee": None,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "dependencies": [],
                "tags": ["strategy"],
            })
    
    return {
        "plan_id": plan_id,
        "startup_id": startup_id,
        "version": 1,
        "title": f"Plan: {goal[:50]}..." if len(goal) > 50 else f"Plan: {goal}",
        "created_at": created_at,
        "time_horizon_days": time_horizon_days,
        "strategy_advice": strategy_advice,
        "phases": phases,
        "tasks": tasks,
    }


# --- API ROUTES ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Agentic Business Ops API is running"}


@app.get("/api/health")
async def health():
    """API health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    startup_id: Optional[str] = Form(None),
):
    """
    Upload a business document (PDF, deck, etc.) and create/update a startup.
    """
    try:
        # Generate startup_id if not provided
        if not startup_id:
            startup_id = str(uuid.uuid4())
        
        # Create startup directory
        startup_dir = ensure_startup_dir(startup_id)
        
        # Save the file
        file_path = startup_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"📄 Uploaded file {file.filename} for startup {startup_id}")
        
        # Also copy to source folder for orchestrator to find
        source_path = SOURCE_DIR / file.filename
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, source_path)
        
        # Create or update basic profile
        existing_profile = get_profile(startup_id)
        if not existing_profile:
            profile_data = {
                "startup_id": startup_id,
                "business_name": "Pending Analysis",
                "business_type": "Startup",
                "location": "Egypt",
                "documents": [file.filename],
            }
            save_profile(profile_data)
        else:
            # Add document to existing profile
            docs = existing_profile.get("documents", [])
            if file.filename not in docs:
                docs.append(file.filename)
                existing_profile["documents"] = docs
                save_profile(existing_profile)
        
        return UploadResponse(
            startup_id=startup_id,
            message=f"File '{file.filename}' uploaded successfully",
        )
    
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a startup using uploaded documents.
    Runs the orchestrator in Q&A mode.
    """
    try:
        logger.info(f"❓ Question for {request.startup_id}: {request.question[:100]}...")
        
        result = run_orchestrator_question(
            startup_id=request.startup_id,
            question=request.question,
        )
        
        return QuestionResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Question error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plan")
async def generate_plan(request: PlanRequest):
    """
    Generate an action plan for a startup.
    Runs the full orchestrator pipeline: onboarding → research → gap analysis → planner.
    """
    try:
        logger.info(f"📋 Plan request for {request.startup_id}: {request.goal[:100]}...")
        
        plan = run_orchestrator_for_plan(
            startup_id=request.startup_id,
            goal=request.goal,
            time_horizon_days=request.time_horizon_days,
        )
        
        return plan
    
    except Exception as e:
        logger.error(f"❌ Plan generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans/{startup_id}")
async def get_startup_plans(startup_id: str, limit: int = 10):
    """Get all plans for a startup."""
    plans = list_plans_for_startup(startup_id, limit)
    return {"startup_id": startup_id, "plans": plans}


@app.get("/api/plan/{plan_id}")
async def get_plan_by_id(plan_id: str):
    """Get a specific plan by ID."""
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.get("/api/profile/{startup_id}")
async def get_startup_profile(startup_id: str):
    """Get a startup's profile."""
    profile = get_profile(startup_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Startup not found")
    return profile


# --- RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
