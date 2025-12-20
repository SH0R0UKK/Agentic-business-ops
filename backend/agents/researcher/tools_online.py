import requests
import json
import logging
from .models import ResearchResult

logger = logging.getLogger(__name__)

class BudgetPerplexitySearcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.perplexity.ai/chat/completions"
        # "sonar" is the cost-effective model (approx $5/1000 searches)
        self.model = "sonar"

    def search(self, query: str, grounding_rules: list, timeout: int = 30) -> ResearchResult | None:
        """
        Fetches data from Perplexity API and validates the JSON structure.
        
        Args:
            query: Research query
            grounding_rules: Constraints for the search
            timeout: Request timeout in seconds (default: 30)
        """
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
            # Note: We rely on the system prompt for JSON, as 'response_format' 
            # support varies by model tier. 
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # --- PARSING & VALIDATION ---
            raw_content = response.json()['choices'][0]['message']['content']
            
            # Clean up potential markdown code blocks (common LLM quirk)
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