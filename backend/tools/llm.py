import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load .env at import time
load_dotenv()

# Model names
_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_SONAR_MODEL = os.getenv("SONAR_MODEL", "sonar-pro")  # New

def _call_openai(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    from openai import OpenAI
    client = OpenAI()
    kwargs = {"model": _OPENAI_MODEL, "messages": messages}
    if response_format:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content

def _call_gemini(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(_GEMINI_MODEL)
    sys = "\n".join(m["content"] for m in messages if m["role"] == "system")
    usr = "\n".join(m["content"] for m in messages if m["role"] == "user")
    prompt = (sys + "\n\n" + usr).strip()
    resp = model.generate_content(prompt)
    return resp.text or "{}"
def _call_sonar(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    """Perplexity Sonar API - uses OpenAI-compatible interface with limitations"""
    from openai import OpenAI
    
    client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai"
    )
    
    # Perplexity doesn't support response_format like OpenAI
    # Instead, we add JSON instruction to the system message
    if response_format and response_format.get("type") == "json":
        # Find system message and append JSON instruction
        for msg in messages:
            if msg["role"] == "system":
                msg["content"] += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations."
                break
    
    # Call WITHOUT response_format parameter
    resp = client.chat.completions.create(
        model=_SONAR_MODEL,
        messages=messages
    )
    
    return resp.choices[0].message.content

# def _call_mock(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
#     import re
#     text = "\n".join(m["content"] for m in messages)
#     try:
#         data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
#     except Exception:
#         data = {}
#     profile = data.get("startup_profile", {})
#     research = data.get("research_summary", {})
#     goal = data.get("user_goal", "")

#     sector = (profile.get("sector") or "general").lower()

#     internal = []
#     market = []

#     def mk_gap(desc, cat, sev="medium", conf=0.7, related=False, threat=""):
#         return {
#             "gap_id": "",
#             "category": cat,
#             "description": desc,
#             "severity": sev,
#             "confidence": conf,
#             "reasoning": "Based on research summary items.",
#             "related_to_goal": related,
#             "competitive_threat": threat,
#             "sources": ["research_summary"]
#         }

#     if sector == "tourism":
#         internal.append(mk_gap("No consistent social media content strategy", "process", "high", 0.8, "marketing" in goal.lower()))
#         internal.append(mk_gap("Marketing budget below industry benchmark", "resource", "high", 0.75, True))
#         market.append(mk_gap("Lower visibility vs competitors' large social following", "positioning", "high", 0.8, True, "competitors' social channels"))
#         market.append(mk_gap("No SEO content while rivals rank for key travel terms", "channels", "medium", 0.7, True, "search ranking"))
#     elif sector == "fintech":
#         internal.append(mk_gap("Missing compliance (SOC2/PCI-DSS)", "process", "critical", 0.85, True))
#         internal.append(mk_gap("Manual onboarding instead of automated KYC/AML", "process", "high", 0.8, True))
#         market.append(mk_gap("No developer docs or API sandbox like top competitors", "features", "high", 0.75, True, "developer-first competitors"))
#         market.append(mk_gap("No uptime SLA vs. 99.99% common in market", "positioning", "medium", 0.7, True, "market SLA norms"))
#     else:
#         internal.append(mk_gap("Lack of documented operating procedures", "process", "medium", 0.65, False))
#         market.append(mk_gap("Unclear differentiation vs. competitors", "positioning", "medium", 0.65, False, "generic competition"))

#     return json.dumps({"internal_gaps": internal, "market_gaps": market})

def call_llm(messages: List[Dict], response_format: Optional[Dict] = None) -> str:
    # Read provider at RUNTIME, not import time
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    
    if provider == "openai":
        return _call_openai(messages, response_format)
    if provider == "gemini":
        return _call_gemini(messages, response_format)
    if provider == "sonar":  
        return _call_sonar(messages, response_format)
    return _call_mock(messages, response_format)
