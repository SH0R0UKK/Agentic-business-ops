import requests
import json
import logging
import os
from .models import ResearchResult, OnlineBenchmarkPack, BenchmarkFinding, BenchmarkSource
from . import llm_client

logger = logging.getLogger(__name__)


class BudgetPerplexitySearcher:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.url = "https://api.perplexity.ai/chat/completions"
        # "sonar" is the cost-effective model (approx $5/1000 searches)
        self.model = os.getenv("PERPLEXITY_MODEL", "sonar")

    def search(self, query: str, grounding_rules: list = None, timeout: int = 30) -> ResearchResult | None:
        """
        Fetches data from Perplexity API and validates the JSON structure.
        
        Args:
            query: Research query
            grounding_rules: Constraints for the search
            timeout: Request timeout in seconds (default: 30)
        """
        if grounding_rules is None:
            grounding_rules = ["Prioritize recent data", "Cite sources"]
            
        logger.info(f"🌐 Searching Online for: {query[:50]}...")

        system_prompt = (
            "You are a precise market researcher. "
            "Return valid JSON ONLY. No markdown formatting. "
            "Schema: {summary: str, key_statistics: [str], citations: [str], confidence_score: int}. "
            f"Constraints: {'; '.join(grounding_rules)}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.2,  # Low temperature = more factual
            "return_citations": True
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            raw_content = response.json()['choices'][0]['message']['content']
            
            # Clean up potential markdown code blocks
            if raw_content.startswith("```json"):
                raw_content = raw_content.replace("```json", "").replace("```", "")
            
            data = json.loads(raw_content)
            
            # Clamp confidence_score to valid range (1-10)
            raw_confidence = data.get("confidence_score", 5)
            confidence = max(1, min(10, int(raw_confidence)))

            return ResearchResult(
                summary=data.get("summary", "No summary provided."),
                key_statistics=data.get("key_statistics", []),
                citations=data.get("citations", []),
                confidence_score=confidence,
                source_type="online"
            )

        except Exception as e:
            logger.error(f"❌ Online Search Failed: {e}")
            return None

    def search_raw(self, query: str, timeout: int = 30) -> list[dict]:
        """
        Fetches raw search results for LLM processing.
        Returns list of dicts with: snippet, url, title, published_at, source_name
        """
        logger.info(f"🌐 Raw search for: {query[:50]}...")
        
        # For Sonar, we ask for a more structured response
        system_prompt = """You are a research assistant. Search for information about the user's query.
Return valid JSON with this structure:
{
    "results": [
        {
            "snippet": "relevant text excerpt",
            "url": "source url",
            "title": "article title",
            "published_at": "date if known or 'unknown'",
            "source_name": "publication name"
        }
    ],
    "summary": "brief overall summary"
}
Include 3-5 most relevant results."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.2,
            "return_citations": True
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            raw_content = response.json()['choices'][0]['message']['content']
            
            if raw_content.startswith("```json"):
                raw_content = raw_content.replace("```json", "").replace("```", "")
            elif raw_content.startswith("```"):
                raw_content = raw_content.replace("```", "")
            
            data = json.loads(raw_content)
            
            results = data.get("results", [])
            
            # If we got a summary but no structured results, create a single result
            if not results and data.get("summary"):
                results = [{
                    "snippet": data.get("summary", ""),
                    "url": "perplexity_search",
                    "title": query[:50],
                    "published_at": "unknown",
                    "source_name": "Perplexity AI"
                }]
            
            logger.info(f"📋 Retrieved {len(results)} raw results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Raw search failed: {e}")
            return []


async def online_research_with_llm(
    question: str,
    profile_context: dict = None,
    grounding_rules: list = None
) -> OnlineBenchmarkPack:
    """
    High-level function that combines Sonar search with LLM reasoning.
    
    1) Call Sonar Search API.
    2) Normalize results into sonar_items.
    3) Call llm_client.summarize_online_context().
    4) Return a structured OnlineBenchmarkPack.
    
    Args:
        question: User's research question
        profile_context: Optional dict with startup profile info
        grounding_rules: Optional search constraints
    
    Returns:
        OnlineBenchmarkPack with findings, assumptions, disclaimers
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        logger.error("PERPLEXITY_API_KEY not set")
        return OnlineBenchmarkPack(
            question=question,
            summary="API key not configured.",
            findings=[],
            assumptions=[],
            prohibited_uses=["Service unavailable"],
            status="error"
        )
    
    searcher = BudgetPerplexitySearcher(api_key=api_key)
    
    # Step 1: Get raw search results
    sonar_items = searcher.search_raw(question)
    
    if not sonar_items:
        logger.warning("No results from Sonar search")
        return OnlineBenchmarkPack(
            question=question,
            summary="No results found from web search.",
            findings=[],
            assumptions=[],
            prohibited_uses=["No data available"],
            status="no_results"
        )
    
    # Step 2: Call LLM for summarization
    llm_result = await llm_client.summarize_online_context(question, sonar_items)
    
    if not llm_result:
        logger.error("LLM summarization failed")
        return OnlineBenchmarkPack(
            question=question,
            summary="LLM processing failed. Raw results retrieved but not summarized.",
            findings=[],
            assumptions=[],
            prohibited_uses=["Processing error"],
            status="error"
        )
    
    # Step 3: Parse LLM result into Pydantic model
    findings = []
    for f in llm_result.get("findings", []):
        sources = []
        for s in f.get("sources", []):
            sources.append(BenchmarkSource(
                url=s.get("url", ""),
                title=s.get("title", "")
            ))
        
        scope = f.get("scope", "global")
        if scope not in ["egypt", "mena", "global"]:
            scope = "global"
        
        findings.append(BenchmarkFinding(
            pattern=f.get("pattern", ""),
            scope=scope,
            sources=sources,
            approx_date_range=f.get("approx_date_range", "unknown")
        ))
    
    return OnlineBenchmarkPack(
        question=question,
        summary=llm_result.get("summary", ""),
        findings=findings,
        freshness_days=llm_result.get("freshness_days"),
        assumptions=llm_result.get("assumptions", []),
        prohibited_uses=llm_result.get("prohibited_uses", [
            "Not legal advice",
            "Not guaranteed to apply to specific startup",
            "May be outdated",
            "Requires expert validation in Egypt"
        ]),
        status="success"
    )