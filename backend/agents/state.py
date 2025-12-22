# backend/agents/state.py

from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class MasterState(TypedDict):
    # --- SHARED CONVERSATION HISTORY ---
    messages: Annotated[List[BaseMessage], add_messages]
    
    # --- CONTEXT ---
    user_context: dict  # Business context (can be from onboarding or manually provided)
    
    # --- ONBOARDING STATE (NEW) ---
    onboarding_status: Optional[str]  # "pending", "in_progress", "completed", "skipped"
    onboarding_files: Optional[List[str]]  # File paths to process
    processed_files: Optional[List[dict]]  # Processed file data with text/images
    
    # --- ROUTING CONTROL ---
    next_agent: str       # "onboarding", "planner", "gap_agent", "researcher", "research"
    action: str           # "route" or "reply"
    iteration_count: Optional[int]  # Safety counter to prevent infinite loops
    
    # --- TASK SPECIFIC INPUTS (Passed to Workers) ---
    task_type: str        # For Planner: "timeline" or "advisory"
    search_query: str     # For Researcher
    
    # --- WORKER OUTPUTS (Data Bubble Up) ---
    final_plan: Optional[dict]        # Output from Planner
    research_data: Optional[str]      # Output from Online Researcher (legacy)
    rag_data: Optional[str]           # Output from Offline RAG (legacy)
    gap_analysis: Optional[str]       # Output from Gap Agent
    
    # --- NEW: Research Agent Outputs (Structured) ---
    research_offline: Optional[dict]  # OfflineEvidencePack from RAG + LLM
    research_online: Optional[dict]   # OnlineBenchmarkPack from Web + LLM
    
    # --- FINAL OUTPUT ---
    final_reply: Optional[str]        # The text the User sees