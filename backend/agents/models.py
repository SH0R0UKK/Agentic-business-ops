"""
Shared input/output models for all agents.
Defines clear contracts between agents and the orchestrator.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


# ============================================================================
# ONBOARDING AGENT MODELS
# ============================================================================

class OnboardingRequest(BaseModel):
    """Input for the Onboarding/Profiling Agent."""
    startup_id: str = Field(..., description="Unique identifier for the startup")
    founder_inputs: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Manual inputs from founder (optional)"
    )
    file_paths: List[str] = Field(
        default_factory=list,
        description="Paths to documents to analyze (PDFs, text, etc.)"
    )


class StartupProfile(BaseModel):
    """Output from the Onboarding Agent - comprehensive startup profile."""
    startup_id: str = Field(..., description="Unique identifier")
    business_name: str = Field(default="", description="Official company/business name")
    business_type: str = Field(default="", description="Industry/sector (e.g., FinTech, E-commerce)")
    sector: str = Field(default="", description="Specific sector/niche")
    location: str = Field(default="Egypt", description="Primary location")
    stage: str = Field(default="", description="Business stage (Idea, MVP, Seed, Series A, etc.)")
    founded: str = Field(default="", description="Year founded")
    
    goals: List[str] = Field(default_factory=list, description="Explicit business goals")
    key_constraints: List[str] = Field(
        default_factory=list,
        description="Budget limits, regulatory issues, resource gaps"
    )
    target_audience: str = Field(default="", description="Primary customer segment")
    competitors: List[str] = Field(default_factory=list, description="Known competitors")
    unique_value: str = Field(default="", description="Unique value proposition")
    team_size: str = Field(default="", description="Number of employees")
    
    # Metadata
    available_documents: List[str] = Field(
        default_factory=list,
        description="Documents analyzed during onboarding"
    )
    confidence: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0,
        description="Confidence in extracted information"
    )
    open_questions: List[str] = Field(
        default_factory=list,
        description="Questions that need clarification"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of profile creation"
    )


# ============================================================================
# RESEARCH AGENT MODELS
# ============================================================================

class ResearchRequest(BaseModel):
    """Input for the Research Agent."""
    startup_id: str = Field(..., description="Unique identifier for the startup")
    question: str = Field(..., description="Research question to answer")
    startup_profile: Optional[StartupProfile] = Field(
        default=None,
        description="Optional startup profile for context"
    )
    search_offline: bool = Field(default=True, description="Search local knowledge base")
    search_online: bool = Field(default=True, description="Search online sources")
    grounding_rules: List[str] = Field(
        default_factory=lambda: ["Prioritize Egypt/MENA context", "Cite sources"],
        description="Research guidelines"
    )


class Claim(BaseModel):
    """A factual claim from research."""
    value: str = Field(..., description="The factual claim")
    source: str = Field(default="", description="Source of the claim")
    url: str = Field(default="", description="Source URL if available")


class BenchmarkFinding(BaseModel):
    """A benchmark finding from online research."""
    pattern: str = Field(..., description="Observed trend or finding")
    scope: Literal["egypt", "mena", "global"] = Field(
        default="global",
        description="Geographic scope"
    )
    sources: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Sources with title and url"
    )


class OfflineEvidencePack(BaseModel):
    """Structured output from offline RAG research."""
    question: str = Field(..., description="Original research question")
    summary: str = Field(..., description="Concise answer based on RAG")
    claims: List[Claim] = Field(default_factory=list, description="Factual claims")
    contradictions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Conflicting information found"
    )
    missing_info: List[str] = Field(
        default_factory=list,
        description="Questions about missing data"
    )
    status: Literal["success", "error", "no_results"] = Field(default="success")


class OnlineBenchmarkPack(BaseModel):
    """Structured output from online research."""
    question: str = Field(..., description="Original research question")
    summary: str = Field(..., description="Concise answer based on web sources")
    findings: List[BenchmarkFinding] = Field(
        default_factory=list,
        description="Benchmark findings"
    )
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    prohibited_uses: List[str] = Field(
        default_factory=list,
        description="Disclaimers about data usage"
    )
    status: Literal["success", "error", "no_results"] = Field(default="success")


class ResearchResponse(BaseModel):
    """Output from the Research Agent."""
    startup_id: str = Field(..., description="Unique identifier")
    question: str = Field(..., description="Research question")
    offline: Optional[OfflineEvidencePack] = Field(
        default=None,
        description="Offline research results"
    )
    online: Optional[OnlineBenchmarkPack] = Field(
        default=None,
        description="Online research results"
    )
    combined_summary: str = Field(
        default="",
        description="Combined summary of offline + online research"
    )
    confidence_score: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Overall confidence in research (1-10)"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp"
    )


# ============================================================================
# PLANNER AGENT MODELS
# ============================================================================

class PlanRequest(BaseModel):
    """Input for the Planner Agent."""
    startup_id: str = Field(..., description="Unique identifier for the startup")
    startup_profile: StartupProfile = Field(..., description="Startup profile")
    research_offline: Optional[OfflineEvidencePack] = Field(
        default=None,
        description="Offline research results to incorporate"
    )
    research_online: Optional[OnlineBenchmarkPack] = Field(
        default=None,
        description="Online research results to incorporate"
    )
    time_horizon_days: int = Field(
        default=90,
        description="Planning time horizon in days"
    )
    task_type: Literal["timeline", "advisory"] = Field(
        default="advisory",
        description="Type of plan to generate"
    )
    user_question: Optional[str] = Field(
        default=None,
        description="Optional specific question from user"
    )


class Task(BaseModel):
    """A single task in a plan."""
    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Detailed description")
    owner: str = Field(default="", description="Responsible party")
    start_date: Optional[str] = Field(default=None, description="Task start date (ISO)")
    end_date: Optional[str] = Field(default=None, description="Task end date (ISO)")
    status: Literal["pending", "in_progress", "completed"] = Field(default="pending")
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of task IDs this depends on"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class Phase(BaseModel):
    """A phase in a plan containing multiple tasks."""
    id: str = Field(..., description="Unique phase identifier")
    name: str = Field(..., description="Phase name")
    description: str = Field(..., description="Phase description")
    start_date: Optional[str] = Field(default=None, description="Phase start date (ISO)")
    end_date: Optional[str] = Field(default=None, description="Phase end date (ISO)")
    tasks: List[Task] = Field(default_factory=list, description="Tasks in this phase")


class Plan(BaseModel):
    """Output from the Planner Agent."""
    plan_id: str = Field(..., description="Unique plan identifier")
    startup_id: str = Field(..., description="Associated startup")
    version: int = Field(default=1, description="Plan version number")
    title: str = Field(..., description="Plan title")
    summary: str = Field(..., description="Executive summary")
    
    time_horizon_days: int = Field(default=90, description="Planning horizon")
    phases: List[Phase] = Field(default_factory=list, description="Plan phases")
    
    # Alternative format for simple advisory plans (no timeline)
    strategy_advice: Optional[str] = Field(
        default=None,
        description="Strategic advice (for advisory-type plans)"
    )
    schedule_events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Calendar events (for timeline-type plans)"
    )
    
    # Metadata
    chat_summary: str = Field(
        default="",
        description="Conversational summary for user"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp"
    )
    research_incorporated: bool = Field(
        default=False,
        description="Whether research was used in planning"
    )


# ============================================================================
# ORCHESTRATOR MODELS
# ============================================================================

class OrchestrationRequest(BaseModel):
    """Generic input for the orchestrator."""
    startup_id: str = Field(..., description="Unique identifier")
    user_message: str = Field(..., description="User's question or request")
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )
    startup_profile: Optional[StartupProfile] = Field(
        default=None,
        description="Existing startup profile if available"
    )


class OrchestrationResponse(BaseModel):
    """Generic output from the orchestrator."""
    startup_id: str = Field(..., description="Unique identifier")
    reply: str = Field(..., description="Final response to user")
    startup_profile: Optional[StartupProfile] = Field(
        default=None,
        description="Updated/created profile if relevant"
    )
    research: Optional[ResearchResponse] = Field(
        default=None,
        description="Research performed if relevant"
    )
    plan: Optional[Plan] = Field(
        default=None,
        description="Plan created if relevant"
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Suggested next actions"
    )
