# backend/agents/orchestrator/orchestrator.py

import os
import json
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# --- LOCAL IMPORTS ---
from backend.agents.state import MasterState
from backend.agents.Planner.planner import app_graph as planner_graph 
from backend.agents.researcher.agent import run_research_agent
from .prompts import get_supervisor_prompt

# --- CONFIG ---
llm_supervisor = ChatOpenAI(
    model="sonar-reasoning-pro",  # Better for structured decision-making and JSON output
    temperature=0,
    base_url="https://api.perplexity.ai",
    api_key=os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY"),
    timeout=120,
    max_retries=3,
)

# --- PLACEHOLDER NODES ---
def placeholder_node(state): 
    return {} 


# --- RESEARCH NODE (NEW) ---
def research_node(state: MasterState):
    """
    Research node that calls the Research Agent.
    Runs async research and updates state with structured results.
    """
    print("\n🔬 RESEARCH NODE: Starting research...")
    
    try:
        # Run the async research agent
        research_results = asyncio.run(run_research_agent(state))
        
        print(f"✅ Research complete:")
        print(f"   - Offline status: {research_results.get('research_offline', {}).get('status', 'N/A')}")
        print(f"   - Online status: {research_results.get('research_online', {}).get('status', 'N/A')}")
        
        return research_results
        
    except Exception as e:
        print(f"❌ RESEARCH NODE ERROR: {e}")
        return {
            "research_offline": {
                "question": state.get("search_query", "N/A"),
                "summary": f"Research failed: {str(e)}",
                "claims": [],
                "contradictions": [],
                "missing_info": [],
                "status": "error"
            },
            "research_online": {
                "question": state.get("search_query", "N/A"),
                "summary": f"Research failed: {str(e)}",
                "findings": [],
                "assumptions": [],
                "prohibited_uses": [],
                "status": "error"
            }
        }


# --- SUPERVISOR NODE ---
def supervisor_node(state: MasterState):
    history = state['messages']
    last_user_msg = history[-1].content
    user_context = state.get('user_context') or {}
    
    # 1. Gather Snapshot
    # Check if the planner has finished by looking for the specific key
    final_plan = state.get('final_plan') or {}
    planner_summary = final_plan.get('chat_summary', 'N/A') if isinstance(final_plan, dict) else 'N/A'
    
    # Include research data if available - check for actual content, not just empty dicts
    research_offline = state.get('research_offline')
    research_online = state.get('research_online')
    
    # Only consider research done if we have actual results with status
    offline_done = research_offline and isinstance(research_offline, dict) and research_offline.get('status') == 'success'
    online_done = research_online and isinstance(research_online, dict) and research_online.get('status') == 'success'
    
    if offline_done and online_done:
        research_status = "Offline: success, Online: success"
    elif offline_done:
        research_status = f"Offline: success, Online: pending"
    elif online_done:
        research_status = f"Offline: pending, Online: success"
    else:
        research_status = "N/A"  # No research has been completed yet
    
    context_snapshot = f"""
    - Latest Planner Output: {planner_summary}
    - Research Status: {research_status}
    - Gap Analysis: {state.get('gap_analysis', 'N/A')}
    """

    # 2. Generate Prompt
    prompt_text = get_supervisor_prompt(context_snapshot, last_user_msg, user_context)
    
    # 3. Call LLM (Using HumanMessage to fix 400 error)
    response = llm_supervisor.invoke([HumanMessage(content=prompt_text)])
    
    # 4. Parse JSON - Handle reasoning models that include chain-of-thought before JSON
    try:
        content = response.content
        # Try to extract JSON from response (reasoning models may include thinking before JSON)
        import re
        # Look for JSON block in markdown
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            clean = json_match.group(1).strip()
        else:
            # Look for raw JSON object
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', content, re.DOTALL)
            if json_match:
                clean = json_match.group(0)
            else:
                # Fallback: strip markdown and try direct parse
                clean = content.replace("```json", "").replace("```", "").strip()
        
        decision = json.loads(clean)
    except Exception as e:
        print(f"❌ SUPERVISOR PARSE ERROR: {e}")
        print(f"   Raw response: {response.content[:500]}...")
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
workflow.add_node("research", research_node)  # Research node with LLM reasoning
workflow.add_node("gap_agent", placeholder_node)

workflow.set_entry_point("supervisor")

def router(state: MasterState):
    if state["action"] == "reply":
        return END
    next_agent = state.get("next_agent") or END
    # Normalize researcher -> research for backward compatibility
    if next_agent in ("researcher", "rag_agent"):
        return "research"
    return next_agent

workflow.add_conditional_edges(
    "supervisor",
    router,
    {
        "planner": "planner",
        "research": "research",
        "researcher": "research",  # Alias for backward compatibility
        "rag_agent": "research",   # Alias for backward compatibility  
        "gap_agent": "gap_agent",
        END: END
    }
)

# Return Edges
workflow.add_edge("planner", "supervisor")
workflow.add_edge("research", "supervisor")
workflow.add_edge("gap_agent", "supervisor")

master_app = workflow.compile()