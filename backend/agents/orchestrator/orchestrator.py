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
from backend.agents.onboarding.agent import run_onboarding
from backend.agents.gap_analysis.agent import gap_analysis_node
from .prompts import get_supervisor_prompt

# --- CONFIG ---
llm_supervisor = ChatOpenAI(
    model="sonar-pro",  # Better at following JSON format than sonar-reasoning-pro
    temperature=0,
    base_url="https://api.perplexity.ai",
    api_key=os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY"),
    timeout=120,
    max_retries=3,
)

# --- HELPER FUNCTIONS ---
def force_to_json(raw_response: str, user_msg: str = "", research_status: str = "N/A") -> dict:
    """
    Force any LLM response into valid JSON decision format.
    Tries multiple strategies:
    1. Extract existing JSON
    2. Parse markdown/code blocks
    3. Analyze text content and construct JSON
    4. Apply intelligent defaults based on context
    
    Returns a valid supervisor decision dict with keys: action, next_agent, search_query, reply_text
    """
    import re
    import json
    
    content = raw_response.strip()
    
    # Strategy 1: Remove chain-of-thought tags
    content = re.sub(r'<think>[\s\S]*?</think>\s*', '', content, flags=re.DOTALL | re.MULTILINE)
    content = content.strip()
    
    # Strategy 2: Extract JSON from markdown code blocks
    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except:
            pass
    
    # Strategy 3: Find JSON object anywhere in text
    json_match = re.search(r'\{[\s\S]*?"action"[\s\S]*?\}', content, re.DOTALL)
    if json_match:
        try:
            # Extract complete JSON by counting braces
            start = json_match.start()
            brace_count = 0
            end = start
            for i in range(start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            json_str = content[start:end]
            return json.loads(json_str)
        except:
            pass
    
    # Strategy 4: Look for any JSON-like structure
    if '{' in content and '}' in content:
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            return json.loads(content[start:end])
        except:
            pass
    
    # Strategy 5: Analyze text content and construct JSON
    content_lower = content.lower()
    user_lower = user_msg.lower()
    
    # Check research status
    research_done = 'success' in research_status.lower() or 'complete' in research_status.lower()
    
    # Decision logic based on keywords
    if not research_done and any(word in user_lower for word in ['what', 'how', 'why', 'research', 'find', 'analyze', 'tell me about']):
        # Need research
        search_query = user_msg[:200] if len(user_msg) > 20 else "business analysis market research"
        return {
            "action": "route",
            "next_agent": "researcher",
            "search_query": search_query
        }
    
    elif research_done and any(word in user_lower for word in ['plan', 'create', 'schedule', 'timeline', 'strategy']):
        # Need planning after research
        task_type = "timeline" if any(w in user_lower for w in ['schedule', 'timeline', 'when', 'dates']) else "advisory"
        return {
            "action": "route",
            "next_agent": "planner",
            "task_type": task_type
        }
    
    elif any(word in user_lower for word in ['hi', 'hello', 'thanks', 'thank you', 'bye']):
        # Greeting/chitchat
        return {
            "action": "reply",
            "reply_text": "Hello! How can I help you today?"
        }
    
    else:
        # Default: reply with whatever content we have
        reply_text = content[:500] if len(content) > 0 else "I can help you with research, planning, and business analysis. What would you like to know?"
        return {
            "action": "reply",
            "reply_text": reply_text
        }


# --- PLACEHOLDER NODES ---
def placeholder_node(state): 
    return {} 


# --- ONBOARDING NODE ---
def onboarding_node(state: MasterState):
    """
    Onboarding node that processes files from source folder or state.
    Always runs first to check for business documents.
    """
    from pathlib import Path
    
    print("\n📋 ONBOARDING NODE: Checking for business documents...")
    
    try:
        # Priority 1: Check for files in state
        files = state.get('onboarding_files') or []
        
        # Priority 2: Check source folder if no files in state
        if not files:
            source_dir = Path(__file__).parent.parent.parent.parent / "source"
            if source_dir.exists():
                source_files = [str(f) for f in source_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
                if source_files:
                    print(f"📂 Found {len(source_files)} files in source folder")
                    files = source_files
        
        # If still no files, skip onboarding
        if not files:
            print("⚠️ No files found - skipping onboarding")
            existing_context = state.get('user_context', {})
            if existing_context:
                print(f"   Using existing context: {existing_context.get('business_name', 'N/A')}")
            return {
                "onboarding_status": "skipped",
                "user_context": existing_context
            }
        
        # Run onboarding
        org_id = state.get('user_context', {}).get('org_id', 'default')
        result = run_onboarding(file_paths=files, org_id=org_id)
        
        print(f"✅ Onboarding complete: {result['user_context'].get('business_name', 'N/A')}")
        
        return {
            "user_context": result['user_context'],
            "processed_files": result['processed_files'],
            "onboarding_status": "completed"
        }
        
    except Exception as e:
        print(f"❌ ONBOARDING NODE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "onboarding_status": "error",
            "user_context": state.get('user_context', {}),
            "final_reply": f"Onboarding failed: {str(e)}"
        }


# --- RESEARCH NODE ---
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
    
    # Safety: Prevent infinite loops
    iteration_count = state.get('iteration_count', 0)
    if iteration_count >= 10:
        print("⚠️ Max iterations reached, ending workflow")
        return {
            "action": "reply",
            "final_reply": "I've completed the research and analysis. Please let me know if you need anything else."
        }
    
    # 1. Gather Snapshot
    # Check if the planner has finished by looking for the specific key
    final_plan = state.get('final_plan') or {}
    planner_summary = final_plan.get('chat_summary', 'N/A') if isinstance(final_plan, dict) else 'N/A'
    
    # Include research data if available - check for actual content, not just empty dicts
    research_offline = state.get('research_offline')
    research_online = state.get('research_online')
    
    # Only consider research done if we have actual results with status
    offline_done = research_offline and isinstance(research_offline, dict) and research_offline.get('status') in ['success', 'no_results']
    online_done = research_online and isinstance(research_online, dict) and research_online.get('status') in ['success', 'no_results']
    
    # If either research succeeded OR both attempted (including no_results), consider research done
    research_complete = (offline_done or online_done) or (
        research_offline and research_online and 
        research_offline.get('status') and research_online.get('status')
    )
    
    if offline_done and online_done:
        research_status = "Offline: success, Online: success - RESEARCH COMPLETE"
    elif research_complete:
        research_status = "Research completed (at least one source successful)"
    elif offline_done:
        research_status = f"Offline: success, Online: pending"
    elif online_done:
        research_status = f"Offline: pending, Online: success"
    else:
        research_status = "N/A"  # No research has been completed yet
    
    # Check gap analysis completion
    internal_gaps = state.get('internal_gaps', [])
    market_gaps = state.get('market_gaps', [])
    
    if internal_gaps or market_gaps:
        gap_status = f"{len(internal_gaps)} internal gaps, {len(market_gaps)} market gaps identified - GAP ANALYSIS COMPLETE"
    else:
        gap_status = "None"
    
    context_snapshot = f"""
    - Latest Planner Output: {planner_summary}
    - Research Status: {research_status}
    - Gap Analysis: {gap_status}
    """

    # 2. Generate Prompt
    prompt_text = get_supervisor_prompt(context_snapshot, last_user_msg, user_context)
    
    # 3. Call LLM (Using HumanMessage to fix 400 error)
    response = llm_supervisor.invoke([HumanMessage(content=prompt_text)])
    
    # 4. Force response to JSON format (handles all edge cases)
    try:
        decision = force_to_json(response.content, last_user_msg, research_status)
        print(f"\n👔 SUPERVISOR DECISION: {decision.get('action').upper()} -> {decision.get('next_agent', 'USER').upper()}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR in force_to_json: {e}")
        # Ultimate fallback
        decision = {"action": "reply", "reply_text": "I'm experiencing technical difficulties. Please try rephrasing your request."}

    # 5. Return Updates
    return {
        "action": decision.get("action"),
        "next_agent": decision.get("next_agent"),
        "search_query": decision.get("search_query"),
        "final_reply": decision.get("reply_text"),
        "iteration_count": iteration_count + 1
    }

# --- BUILD GRAPH ---
workflow = StateGraph(MasterState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("onboarding", onboarding_node)  # Onboarding node
workflow.add_node("planner", planner_graph)
workflow.add_node("research", research_node)  # Research node with LLM reasoning
workflow.add_node("gap_agent", gap_analysis_node)  # Gap analysis node

# Entry point: ALWAYS start with onboarding to check for source files
def entry_router(state: MasterState):
    """
    Always route to onboarding first.
    Onboarding will check for files in source folder or state.
    If no files found, it will skip and pass through to supervisor.
    """
    return "onboarding"

workflow.set_conditional_entry_point(entry_router, {
    "onboarding": "onboarding"
})

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
workflow.add_edge("onboarding", "supervisor")  # After onboarding, go to supervisor
workflow.add_edge("planner", "supervisor")
workflow.add_edge("research", "supervisor")
workflow.add_edge("gap_agent", "supervisor")

master_app = workflow.compile()