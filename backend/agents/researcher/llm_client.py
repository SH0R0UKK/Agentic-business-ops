"""
LLM Client for Research Agent
Wraps Perplexity Sonar Reasoning API for structured summarization.
"""

import os
import json
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration via environment variables
LLM_API_KEY = os.getenv("PERPLEXITY_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.perplexity.ai/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "sonar")

SYSTEM_PROMPT_BASE = """You are a cautious research assistant. You receive a user question and several context passages with citations.

RULES:
- Use ONLY the provided passages. Do NOT invent information.
- If information is missing or uncertain, list explicit follow-up questions or mark fields as "unknown".
- Output strictly in JSON with the schema you are given.
- Do NOT invent legal, regulatory, or fundraising conclusions; instead, mark them as "requires expert validation in Egypt".
- Be specific about sources and cite chunk_id or url for each claim."""


OFFLINE_SCHEMA = """{
    "summary": "string - concise answer to the question",
    "claims": [
        {
            "value": "string - the factual claim",
            "source_chunk_id": "string - chunk ID from context",
            "url": "string - source URL",
            "doc_type": "string - document type"
        }
    ],
    "contradictions": [
        {
            "claim_a": "string - first conflicting claim",
            "claim_b": "string - second conflicting claim",
            "source_a": "string - source of first claim",
            "source_b": "string - source of second claim"
        }
    ],
    "missing_info": ["string - questions about missing data"]
}"""


ONLINE_SCHEMA = """{
    "summary": "string - concise answer based on web sources",
    "findings": [
        {
            "pattern": "string - observed trend or finding",
            "scope": "egypt | mena | global",
            "sources": [{"url": "string", "title": "string"}],
            "approx_date_range": "string - e.g., 2023-2024"
        }
    ],
    "freshness_days": "int or null - approximate age of most recent source",
    "assumptions": ["string - assumptions made in analysis"],
    "prohibited_uses": ["string - disclaimers about data usage"]
}"""


async def _call_llm(messages: list[dict], max_retries: int = 2) -> Optional[dict]:
    """Internal function to call LLM API with retry logic."""
    
    if not LLM_API_KEY:
        logger.error("LLM_API_KEY not set")
        return None
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.1
    }
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(LLM_API_URL, json=payload, headers=headers)
                response.raise_for_status()
                
                raw_content = response.json()["choices"][0]["message"]["content"]
                
                # Clean markdown code blocks
                if raw_content.startswith("```json"):
                    raw_content = raw_content.replace("```json", "").replace("```", "")
                elif raw_content.startswith("```"):
                    raw_content = raw_content.replace("```", "")
                
                return json.loads(raw_content.strip())
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                # Add stricter instruction for retry
                messages[-1]["content"] += "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanation."
            else:
                logger.error("Failed to parse JSON after retries")
                return None
                
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None
    
    return None


async def summarize_offline_context(question: str, context_chunks: list[dict]) -> Optional[dict]:
    """
    Summarize RAG chunks using LLM.
    
    Args:
        question: User's research question
        context_chunks: List of dicts with keys: chunk_id, text, source_title, url, doc_type, language, scope
    
    Returns:
        Structured dict matching OfflineEvidencePack schema
    """
    
    # Build context string
    context_text = ""
    for i, chunk in enumerate(context_chunks):
        context_text += f"\n--- CHUNK {i+1} ---\n"
        context_text += f"chunk_id: {chunk.get('chunk_id', 'unknown')}\n"
        context_text += f"source: {chunk.get('source_title', 'Unknown')}\n"
        context_text += f"url: {chunk.get('url', 'N/A')}\n"
        context_text += f"doc_type: {chunk.get('doc_type', 'unknown')}\n"
        context_text += f"language: {chunk.get('language', 'en')}\n"
        context_text += f"text: {chunk.get('text', '')}\n"
    
    system_prompt = SYSTEM_PROMPT_BASE + f"""

TASK: Analyze the following RAG context chunks to answer the user's question.
OUTPUT SCHEMA (respond with this exact JSON structure):
{OFFLINE_SCHEMA}

INSTRUCTIONS:
- For each factual claim, attach the chunk_id and url from the source chunk.
- If chunks contain conflicting information, add to contradictions.
- If data is missing for a complete answer, list specific follow-up questions in missing_info."""

    user_prompt = f"""QUESTION: {question}

CONTEXT PASSAGES:
{context_text}

Analyze these passages and respond with the JSON schema provided."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    result = await _call_llm(messages)
    
    if result:
        # Ensure required fields exist
        result.setdefault("summary", "Unable to summarize")
        result.setdefault("claims", [])
        result.setdefault("contradictions", [])
        result.setdefault("missing_info", [])
        result["question"] = question
    
    return result


async def summarize_online_context(question: str, sonar_items: list[dict]) -> Optional[dict]:
    """
    Summarize Sonar search results using LLM.
    
    Args:
        question: User's research question
        sonar_items: List of dicts with keys: snippet, url, title, published_at, source_name
    
    Returns:
        Structured dict matching OnlineBenchmarkPack schema
    """
    
    # Build context string
    context_text = ""
    for i, item in enumerate(sonar_items):
        context_text += f"\n--- SOURCE {i+1} ---\n"
        context_text += f"title: {item.get('title', 'Unknown')}\n"
        context_text += f"url: {item.get('url', 'N/A')}\n"
        context_text += f"source_name: {item.get('source_name', 'Unknown')}\n"
        context_text += f"published_at: {item.get('published_at', 'Unknown')}\n"
        context_text += f"snippet: {item.get('snippet', '')}\n"
    
    system_prompt = SYSTEM_PROMPT_BASE + f"""

TASK: Analyze the following web search results to answer the user's question.
OUTPUT SCHEMA (respond with this exact JSON structure):
{ONLINE_SCHEMA}

INSTRUCTIONS:
- Treat web data as benchmarks only, NOT as absolute truth.
- For each finding, include the pattern, scope (egypt/mena/global), sources, and approximate date range.
- ALWAYS include these prohibited_uses:
  * "Not legal advice"
  * "Not guaranteed to apply to specific startup"
  * "May be outdated"
  * "Requires expert validation in Egypt"
- Be conservative with claims. If uncertain, mark as assumption."""

    user_prompt = f"""QUESTION: {question}

WEB SEARCH RESULTS:
{context_text}

Analyze these web results and respond with the JSON schema provided."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    result = await _call_llm(messages)
    
    if result:
        # Ensure required fields exist
        result.setdefault("summary", "Unable to summarize")
        result.setdefault("findings", [])
        result.setdefault("freshness_days", None)
        result.setdefault("assumptions", [])
        result.setdefault("prohibited_uses", [
            "Not legal advice",
            "Not guaranteed to apply to specific startup",
            "May be outdated",
            "Requires expert validation in Egypt"
        ])
        result["question"] = question
    
    return result
