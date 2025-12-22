import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# --- LOCAL IMPORTS ---
from backend.agents.state import MasterState
from backend.agents.Planner.planner import app_graph as planner_graph 
# FIX 1: Import the new Template Object, NOT the old function
from .prompts import supervisor_prompt_template 

# --- CONFIG ---
llm_supervisor = ChatOpenAI(
    model="sonar-reasoning-pro",
    temperature=0,
    openai_api_base="https://api.perplexity.ai",
    openai_api_key=os.getenv("PPLX_API_KEY"),
    request_timeout=120,
    max_retries=3
)

# --- PLACEHOLDER NODES ---
def placeholder_node(state): return {} 

# --- SUPERVISOR NODE ---
def supervisor_node(state: MasterState):
    history = state['messages']
    last_user_msg = history[-1].content
    user_context = state.get('user_context', {})
    
    # 1. Gather Context Snapshot
    planner_summary = state.get('final_plan', {}).get('chat_summary', 'N/A')
    
    context_snapshot = f"""
    - Latest Planner Output: {planner_summary}
    - Research/Gap Data: N/A
    """

    # 2. Prepare Variables (Logic moved here to avoid "ValueError" in templates)
    # FIX 2: We calculate the strings here, so the prompt just sees clean variables
   # 2. Prepare Variables
    prompt_variables = {
        # CHANGE THIS: Use 'biz_name' to match the {biz_name} in your template
        "biz_name": user_context.get('business_name', 'The Business'),
        
        # CHANGE THIS: Use 'biz_type' to match the {biz_type} in your template
        "biz_type": user_context.get('business_type', 'General Business'),
        
        "goals": str(user_context.get('goals', 'Improve operations')),
        "context_snapshot": context_snapshot,
        "user_msg": last_user_msg
    }
    # 3. Create Chain & Invoke
    # FIX 3: Use the chain (Template | LLM)
    chain = supervisor_prompt_template | llm_supervisor
    
    # We pass the dictionary of variables
    response = chain.invoke(prompt_variables)
    
    # --- METRICS: CITATION EXTRACTION ---
    citations = response.response_metadata.get('citations', [])
    confidence_score = 0.0
    if citations:
        trusted_domains = [".gov", ".edu", "reuters.com", "bloomberg.com", "nytimes.com"]
        trusted_count = sum(1 for url in citations if any(d in url for d in trusted_domains))
        confidence_score = round(trusted_count / len(citations), 2)
        print(f"  📊 \033[96mSources Found: {len(citations)} | Confidence: {confidence_score}\033[0m")
    # ------------------------------------

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
        "search_query": decision.get("search_query"),
        "final_reply": decision.get("reply_text"),
        "citations": citations,
        "confidence_score": confidence_score
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

workflow.add_edge("planner", "supervisor")
workflow.add_edge("gap_agent", "supervisor")
workflow.add_edge("researcher", "supervisor")
workflow.add_edge("rag_agent", "supervisor")

master_app = workflow.compile()