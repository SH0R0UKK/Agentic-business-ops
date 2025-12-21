# backend/agents/state.py

from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class MasterState(TypedDict):
    # --- SHARED CONVERSATION HISTORY ---
    messages: Annotated[List[BaseMessage], add_messages]
    
    # --- CONTEXT ---
    user_context: dict
    
    # --- ROUTING CONTROL ---
    next_agent: str       # "planner", "gap_agent", "researcher", "rag_agent"
    action: str           # "route" or "reply"
    
    # --- TASK SPECIFIC INPUTS (Passed to Workers) ---
    task_type: str        # For Planner: "timeline" or "advisory"
    search_query: str     # For Researcher
    
    # --- WORKER OUTPUTS (Data Bubble Up) ---
    final_plan: Optional[dict]        # Output from Planner
    research_data: Optional[str]      # Output from Online Researcher
    rag_data: Optional[str]           # Output from Offline RAG
    gap_analysis: Optional[str]       # Output from Gap Agent
    
    # --- FINAL OUTPUT ---
    final_reply: Optional[str]        # The text the User sees