"""
FastAPI Backend for Agentic Business Ops Platform.
Provides HTTP endpoints for the frontend to interact with agents.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import agent models
from backend.agents.models import (
    OnboardingRequest, StartupProfile,
    ResearchRequest, ResearchResponse,
    PlanRequest, Plan,
    OrchestrationRequest, OrchestrationResponse
)

# Import agent functions
from backend.agents.onboarding.agent import run_onboarding
from backend.agents.researcher.agent import run_research_agent
from backend.agents.Planner.planner import app_graph as planner_graph
from backend.agents.orchestrator.orchestrator import master_app
from backend.tools.tracing import trace_run, log_event

# Database utilities
from backend.data.db.storage import (
    init_db, save_profile, get_profile, save_plan, get_plan, get_latest_plan
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Business Ops API",
    description="AI-powered business consultancy for Egyptian startups",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and ensure data directories exist."""
    logger.info("🚀 Starting Agentic Business Ops API...")
    
    # Initialize database
    init_db()
    
    # Ensure data directories exist
    data_dir = Path(__file__).parent / "data"
    (data_dir / "db").mkdir(parents=True, exist_ok=True)
    (data_dir / "benchmark_sources").mkdir(parents=True, exist_ok=True)
    (data_dir / "test_documents").mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ API ready to serve requests")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Agentic Business Ops API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "agents": {
            "onboarding": "ready",
            "researcher": "ready",
            "planner": "ready",
            "orchestrator": "ready"
        }
    }


# ============================================================================
# ONBOARDING ENDPOINT
# ============================================================================

@app.post("/api/onboarding", response_model=StartupProfile)
async def create_startup_profile(
    startup_id: str = Body(...),
    founder_inputs: Dict[str, Any] = Body(default={}),
    uploaded_files: Optional[list] = Body(default=None)
):
    """
    Onboarding endpoint - creates a startup profile.
    
    Processes uploaded documents and founder inputs to extract business context.
    """
    with trace_run("api_onboarding", metadata={"startup_id": startup_id}):
        try:
            logger.info(f"📋 Onboarding request for startup: {startup_id}")
            
            # Collect file paths
            file_paths = []
            
            # Check for files in request
            if uploaded_files:
                file_paths.extend(uploaded_files)
            
            # Check source folder
            source_dir = Path(__file__).parent.parent / "source"
            if source_dir.exists():
                source_files = [
                    str(f) for f in source_dir.iterdir() 
                    if f.is_file() and not f.name.startswith('.')
                ]
                file_paths.extend(source_files)
            
            if not file_paths and not founder_inputs:
                raise HTTPException(
                    status_code=400,
                    detail="No files or founder inputs provided"
                )
            
            # Run onboarding agent
            log_event("onboarding_start", {"file_count": len(file_paths)})
            
            result = run_onboarding(
                file_paths=file_paths,
                org_id=startup_id
            )
            
            # Convert to StartupProfile model
            profile = StartupProfile(
                startup_id=startup_id,
                **result['user_context']
            )
            
            # Save to database
            save_profile(profile.model_dump())
            
            log_event("onboarding_complete", {"profile_created": True})
            logger.info(f"✅ Profile created for: {profile.business_name}")
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Onboarding error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/{startup_id}", response_model=StartupProfile)
async def get_startup_profile(startup_id: str):
    """Retrieve an existing startup profile."""
    try:
        profile_data = get_profile(startup_id)
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return StartupProfile(**profile_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RESEARCH ENDPOINT
# ============================================================================

@app.post("/api/research", response_model=ResearchResponse)
async def perform_research(request: ResearchRequest):
    """
    Research endpoint - performs offline and online research.
    
    Searches internal knowledge base and online sources.
    """
    with trace_run("api_research", metadata={"startup_id": request.startup_id}):
        try:
            logger.info(f"🔬 Research request: {request.question[:100]}")
            
            # Retrieve profile if not provided
            profile = request.startup_profile
            if not profile:
                profile_data = get_profile(request.startup_id)
                if profile_data:
                    profile = StartupProfile(**profile_data)
            
            # Build state for research agent
            state = {
                "search_query": request.question,
                "user_context": profile.model_dump() if profile else {},
                "startup_id": request.startup_id
            }
            
            # Run research agent
            log_event("research_start", {"question": request.question})
            
            import asyncio
            result = await run_research_agent(state)
            
            # Build response
            response = ResearchResponse(
                startup_id=request.startup_id,
                question=request.question,
                offline=result.get("research_offline"),
                online=result.get("research_online"),
                combined_summary=(
                    result.get("research_offline", {}).get("summary", "") + "\n\n" +
                    result.get("research_online", {}).get("summary", "")
                )
            )
            
            log_event("research_complete", {
                "offline_status": result.get("research_offline", {}).get("status"),
                "online_status": result.get("research_online", {}).get("status")
            })
            
            logger.info(f"✅ Research complete")
            return response
            
        except Exception as e:
            logger.error(f"❌ Research error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PLANNER ENDPOINT
# ============================================================================

@app.post("/api/plan", response_model=Plan)
async def create_plan(request: PlanRequest):
    """
    Planner endpoint - generates a strategic plan.
    
    Creates timeline-based or advisory plans based on research and profile.
    """
    with trace_run("api_plan", metadata={"startup_id": request.startup_id}):
        try:
            logger.info(f"📅 Plan request for: {request.startup_id}")
            
            # Build state for planner
            from langchain_core.messages import HumanMessage
            
            user_message = request.user_question or "Create a strategic plan"
            
            state = {
                "messages": [HumanMessage(content=user_message)],
                "user_context": request.startup_profile.model_dump(),
                "research_offline": (
                    request.research_offline.model_dump() 
                    if request.research_offline else None
                ),
                "research_online": (
                    request.research_online.model_dump() 
                    if request.research_online else None
                ),
                "final_plan": None
            }
            
            # Run planner
            log_event("planner_start", {"task_type": request.task_type})
            
            result = planner_graph.invoke(state)
            
            plan_data = result.get("final_plan", {})
            if not plan_data:
                raise ValueError("Planner did not return a plan")
            
            # Convert to Plan model
            import uuid
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                startup_id=request.startup_id,
                title=plan_data.get("chat_summary", "Strategic Plan"),
                summary=plan_data.get("chat_summary", ""),
                strategy_advice=plan_data.get("strategy_advice"),
                schedule_events=plan_data.get("schedule_events", []),
                time_horizon_days=request.time_horizon_days,
                research_incorporated=bool(request.research_offline or request.research_online)
            )
            
            # Save to database
            save_plan(plan.model_dump())
            
            log_event("planner_complete", {"plan_id": plan.plan_id})
            logger.info(f"✅ Plan created: {plan.plan_id}")
            
            return plan
            
        except Exception as e:
            logger.error(f"❌ Planner error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans/{startup_id}", response_model=Plan)
async def get_plan_by_startup(startup_id: str):
    """Retrieve the latest plan for a startup."""
    try:
        plan_data = get_latest_plan(startup_id)
        if not plan_data:
            raise HTTPException(status_code=404, detail="No plan found for this startup")
        
        return Plan(**plan_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plan/{plan_id}", response_model=Plan)
async def get_plan_by_id(plan_id: str):
    """Retrieve a specific plan by ID."""
    try:
        plan_data = get_plan(plan_id)
        if not plan_data:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return Plan(**plan_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ORCHESTRATOR ENDPOINT (Full conversation)
# ============================================================================

@app.post("/api/chat", response_model=OrchestrationResponse)
async def chat_with_orchestrator(request: OrchestrationRequest):
    """
    Orchestrator endpoint - handles conversational interactions.
    
    Routes to appropriate agents based on user intent.
    """
    with trace_run("api_orchestrator", metadata={"startup_id": request.startup_id}):
        try:
            logger.info(f"💬 Chat request from: {request.startup_id}")
            
            # Build state for orchestrator
            from langchain_core.messages import HumanMessage
            
            messages = [HumanMessage(content=msg["content"]) for msg in request.conversation_history]
            messages.append(HumanMessage(content=request.user_message))
            
            state = {
                "messages": messages,
                "user_context": (
                    request.startup_profile.model_dump() 
                    if request.startup_profile else {}
                ),
                "action": None,
                "next_agent": None,
                "final_reply": None,
                "final_plan": None,
                "research_offline": None,
                "research_online": None
            }
            
            # Run orchestrator
            log_event("orchestrator_start", {"message": request.user_message})
            
            result = master_app.invoke(state)
            
            # Build response
            response = OrchestrationResponse(
                startup_id=request.startup_id,
                reply=result.get("final_reply", ""),
                startup_profile=(
                    StartupProfile(**result["user_context"]) 
                    if result.get("user_context") else None
                ),
                plan=(
                    Plan(**result["final_plan"]) 
                    if result.get("final_plan") else None
                )
            )
            
            log_event("orchestrator_complete", {"action": result.get("action")})
            logger.info(f"✅ Chat complete")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Orchestrator error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    logger.info(f"🚀 Starting server on port {port}")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Disable in production
    )
