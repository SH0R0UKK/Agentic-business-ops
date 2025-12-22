# backend/agents/orchestrator/orchestrator.py

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage # <--- Ensure HumanMessage is imported
from langgraph.graph import StateGraph, END

# --- LOCAL IMPORTS ---
from backend.agents.state import MasterState
from backend.agents.Planner.planner import app_graph as planner_graph 
from .prompts import get_supervisor_prompt

# --- CONFIG ---
llm_supervisor = ChatOpenAI(
    model="sonar-pro",
    temperature=0,
    openai_api_base="https://api.perplexity.ai",
    openai_api_key=os.getenv("PPLX_API_KEY"),
    # --- ADD THESE LINES ---
    request_timeout=120,      # Give it 2 minutes to search/think
    max_retries=3,            # Try 3 times if connection drops
)

# --- PLACEHOLDER NODES ---
def placeholder_node(state): return {} 

# --- SUPERVISOR NODE ---
def supervisor_node(state: MasterState):
    history = state['messages']
    last_user_msg = history[-1].content
    user_context = state.get('user_context', {})
    
    # 1. Gather Snapshot
    # Check if the planner has finished by looking for the specific key
    planner_summary = state.get('final_plan', {}).get('chat_summary', 'N/A')
    
    context_snapshot = f"""
    - Latest Planner Output: {planner_summary}
    - Research/Gap Data: N/A
    """

    # 2. Generate Prompt
    prompt_text = get_supervisor_prompt(context_snapshot, last_user_msg, user_context)
    
    # 3. Call LLM (Using HumanMessage to fix 400 error)
    response = llm_supervisor.invoke([HumanMessage(content=prompt_text)])
    
    # 4. Parse JSON
    try:
        clean = response.content.replace("```json", "").replace("```", "").strip()
        decision = json.loads(clean)
    except Exception as e:
        print(f"❌ SUPERVISOR PARSE ERROR: {e}")
        decision = {"action": "reply", "reply_text": "I encountered a system error."}

    print(f"\n👔 SUPERVISOR DECISION: {decision.get('action').upper()} -> {decision.get('next_agent', 'USER').upper()}")

    # 5. Return Updates
    return {
        "action": decision.get("action"),
        "next_agent": decision.get("next_agent"),
        # REMOVED: "task_type": ... (The Planner handles this now)
        "search_query": decision.get("search_query"),
        "final_reply": decision.get("reply_text")
    }

# --- BUILD GRAPH ---
workflow = StateGraph(MasterState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("planner", planner_graph)
workflow.add_node("gap_agent", placeholder_node)
workflow.add_node("researcher", placeholder_node)
workflow.add_node("rag_agent", placeholder_node)

workflow.set_entry_point("supervisor")

def router(state: MasterState):
    if state["action"] == "reply":
        return END
    # Safety: Default to USER if next_agent is None
    return state.get("next_agent") or END

workflow.add_conditional_edges(
    "supervisor",
    router,
    {
        "planner": "planner",
        "gap_agent": "gap_agent",
        "researcher": "researcher",
        "rag_agent": "rag_agent",
        END: END
    }
)

# Return Edges
workflow.add_edge("planner", "supervisor")
workflow.add_edge("gap_agent", "supervisor")
workflow.add_edge("researcher", "supervisor")
workflow.add_edge("rag_agent", "supervisor")

master_app = workflow.compile()