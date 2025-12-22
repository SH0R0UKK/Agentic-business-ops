import os
import json
from typing import List, Dict, Optional

# Optional deps are imported lazily
_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()  # "openai" | "gemini" | "mock"
_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")  # Updated model name

def _call_openai(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    from openai import OpenAI
    client = OpenAI()
    kwargs = {"model": _OPENAI_MODEL, "messages": messages}
    if response_format:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content

def _call_gemini(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    """Updated to use new google.genai package"""
    from google import genai
    from google.genai import types
    
    # Initialize client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Flatten messages to a simple prompt
    sys = "\n".join(m["content"] for m in messages if m["role"] == "system")
    usr = "\n".join(m["content"] for m in messages if m["role"] == "user")
    prompt = (sys + "\n\n" + usr).strip()
    
    # Configure for JSON output if requested
    config = None
    if response_format:
        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    
    # Call Gemini
    response = client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=prompt,
        config=config
    )
    
    return response.text or "{}"

def _call_mock(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    # Deterministic, evidence-driven simple synthesis for offline dev
    import re
    text = "\n".join(m["content"] for m in messages)
    try:
        data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
    except Exception:
        data = {}
    profile = data.get("startup_profile", {})
    research = data.get("research_summary", {})
    goal = data.get("user_goal", "")

    sector = (profile.get("sector") or "general").lower()
    stage = (profile.get("stage") or "pre-seed").lower()

    internal = []
    market = []

    def mk_gap(desc, cat, sev="medium", conf=0.7, related=False, threat=""):
        return {
            "gap_id": "",
            "category": cat,
            "description": desc,
            "severity": sev,
            "confidence": conf,
            "reasoning": "Based on research summary items.",
            "related_to_goal": related,
            "competitive_threat": threat,
            "sources": ["research_summary"]
        }

    if sector == "tourism":
        internal.append(mk_gap("No consistent social media content strategy", "process", "high", 0.8, "marketing" in goal.lower()))
        internal.append(mk_gap("Marketing budget below industry benchmark", "resource", "high", 0.75, True))
        market.append(mk_gap("Lower visibility vs competitors' large social following", "positioning", "high", 0.8, True, "competitors' social channels"))
        market.append(mk_gap("No SEO content while rivals rank for key travel terms", "channels", "medium", 0.7, True, "search ranking"))
    elif sector == "fintech":
        internal.append(mk_gap("Missing compliance (SOC2/PCI-DSS)", "process", "critical", 0.85, True))
        internal.append(mk_gap("Manual onboarding instead of automated KYC/AML", "process", "high", 0.8, True))
        market.append(mk_gap("No developer docs or API sandbox like top competitors", "features", "high", 0.75, True, "developer-first competitors"))
        market.append(mk_gap("No uptime SLA vs. 99.99% common in market", "positioning", "medium", 0.7, True, "market SLA norms"))
    else:
        internal.append(mk_gap("Lack of documented operating procedures", "process", "medium", 0.65, False))
        market.append(mk_gap("Unclear differentiation vs. competitors", "positioning", "medium", 0.65, False, "generic competition"))

    return json.dumps({"internal_gaps": internal, "market_gaps": market})

def call_llm(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    if _PROVIDER == "openai":
        return _call_openai(messages, response_format)
    if _PROVIDER == "gemini":
        return _call_gemini(messages, response_format)
    return _call_mock(messages, response_format)
