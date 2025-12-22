import os, json, uuid
from datetime import datetime
from typing import Dict, List
from tools.llm import call_llm
from tools.validators import filter_and_cap_gaps

# LangSmith tracing via env, as commonly done with LangGraph/LangChain stacks.[web:54]
PROJECT = os.getenv("LANGCHAIN_PROJECT", "Agentic_business_ops")

SYSTEM_PROMPT = """You are a startup business analyst. 
Return ONLY JSON with keys: internal_gaps, market_gaps.
Each gap must include: gap_id, category, description, severity, confidence, reasoning, related_to_goal, sources.
Market gaps also include competitive_threat.
- severity ∈ {critical, high, medium, low}
- confidence ∈ [0,1]
- related_to_goal = true if it blocks the stated user_goal.
- sources: list of strings referencing research_summary items (e.g., 'market_trends[0]', 'competitor_analysis[1]').
"""

USER_PROMPT_TEMPLATE = """{{
  "startup_profile": {startup_profile},
  "research_summary": {research_summary},
  "user_goal": "{user_goal}"
}}"""

def _ensure_ids(gaps: List[Dict], prefix: str) -> None:
    for g in gaps:
        if not g.get("gap_id"):
            g["gap_id"] = f"{prefix}-{uuid.uuid4().hex[:8]}"

def _mark_critical_when_goal_blocked(gaps: List[Dict]) -> None:
    for g in gaps:
        if g.get("related_to_goal") and g.get("severity") != "critical":
            g["severity"] = "critical"

def _attach_basic_citations(gaps: List[Dict]) -> None:
    # If sources missing, attach generic pointers so the orchestrator can render citations
    for g in gaps:
        if not g.get("sources"):
            g["sources"] = ["research_summary"]

def gap_analysis_node(state: Dict) -> Dict:
    """
    LangGraph-compatible node function:
    Expects state to contain: startup_profile, research_summary, user_goal
    Produces: internal_gaps, market_gaps, gap_analysis_metadata
    """
    profile = state.get("startup_profile") or {}
    research = state.get("research_summary") or {}
    goal = state.get("user_goal") or ""

    # Build prompt
    user = USER_PROMPT_TEMPLATE.format(
        startup_profile=json.dumps(profile, ensure_ascii=False),
        research_summary=json.dumps(research, ensure_ascii=False),
        user_goal=goal.replace('"', "'")
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user}
    ]

    # Call LLM (OpenAI/Gemini/Mock based on env)
    raw = call_llm(messages, response_format={"type": "json"})
    try:
        parsed = json.loads(raw)
    except Exception:
        # Fallback if model returned text around JSON
        start = raw.find("{"); end = raw.rfind("}")
        parsed = json.loads(raw[start:end+1]) if start != -1 and end != -1 else {"internal_gaps": [], "market_gaps": []}

    internal = parsed.get("internal_gaps", [])
    market = parsed.get("market_gaps", [])

    # Post-process: IDs, citations, critical marking, filter and cap
    _ensure_ids(internal, "INT")
    _ensure_ids(market, "MKT")
    _attach_basic_citations(internal)
    _attach_basic_citations(market)
    _mark_critical_when_goal_blocked(internal)
    _mark_critical_when_goal_blocked(market)

    # Enforce your rules
    min_conf = float(os.getenv("GAP_MIN_CONFIDENCE", "0.5"))
    max_gaps = int(os.getenv("GAP_MAX_TOTAL", "10"))
    internal, market = filter_and_cap_gaps(internal, market, min_confidence=min_conf, max_total=max_gaps)

    # Write back to state
    state["internal_gaps"] = internal
    state["market_gaps"] = market
    state["gap_analysis_metadata"] = {
        "total_gaps_identified": len(internal) + len(market),
        "critical_gaps_count": sum(1 for g in internal+market if g.get("severity") == "critical"),
        "analysis_timestamp": datetime.utcnow().isoformat()
    }
    return state
