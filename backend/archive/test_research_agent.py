"""
Test the enhanced Research Agent with LLM reasoning layer.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from agents.researcher.agent import ResearchAgent
from agents.researcher.models import ResearchTask


async def test_combined_research():
    """Test the new combined research with LLM reasoning."""
    print("=" * 70)
    print("TESTING COMBINED RESEARCH (Offline + Online with LLM)")
    print("=" * 70)
    
    agent = ResearchAgent()
    
    # Test query
    question = "What are the best accelerators for startups in Egypt and what is their application process?"
    
    print(f"\nQuestion: {question}\n")
    print("-" * 70)
    
    # Run combined research
    result = await agent.perform_combined_research(
        question=question,
        startup_context={"stage": "pre-seed", "sector": "fintech"},
        profile_context={"location": "Egypt"}
    )
    
    # Print offline results
    print("\n📚 OFFLINE RESEARCH (RAG Knowledge Base)")
    print("-" * 40)
    if result.offline:
        print(f"Status: {result.offline.status}")
        print(f"Summary: {result.offline.summary[:500]}...")
        print(f"\nClaims ({len(result.offline.claims)}):")
        for claim in result.offline.claims[:3]:
            print(f"  - {claim.value[:100]}...")
            print(f"    Source: {claim.url}")
        print(f"\nMissing Info ({len(result.offline.missing_info)}):")
        for m in result.offline.missing_info[:3]:
            print(f"  - {m}")
    
    # Print online results
    print("\n\n🌐 ONLINE RESEARCH (Web Search)")
    print("-" * 40)
    if result.online:
        print(f"Status: {result.online.status}")
        print(f"Summary: {result.online.summary[:500]}...")
        print(f"\nFindings ({len(result.online.findings)}):")
        for finding in result.online.findings[:3]:
            print(f"  - {finding.pattern}")
            print(f"    Scope: {finding.scope}, Date: {finding.approx_date_range}")
        print(f"\nDisclaimers:")
        for d in result.online.prohibited_uses[:3]:
            print(f"  ⚠️ {d}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return result


def test_legacy_research():
    """Test the legacy simple research flow."""
    print("=" * 70)
    print("TESTING LEGACY RESEARCH FLOW")
    print("=" * 70)
    
    agent = ResearchAgent()
    
    task = ResearchTask(
        query="How to get funding for my fintech startup in Egypt?",
        grounding_rules=["Prioritize Egyptian sources", "Focus on 2023-2024 data"]
    )
    
    print(f"\nQuery: {task.query}")
    print("-" * 70)
    
    result = agent.perform_research(task)
    
    print(f"\nResult:")
    print(f"  Source: {result.source_type}")
    print(f"  Confidence: {result.confidence_score}/10")
    print(f"  Summary: {result.summary[:300]}...")
    print(f"  Citations: {result.citations[:3]}")
    
    print("\n" + "=" * 70)
    return result


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("⚠️ PERPLEXITY_API_KEY not set in environment")
        print("Set it in .env file or environment variables")
        sys.exit(1)
    
    # Test legacy flow
    print("\n\n")
    test_legacy_research()
    
    # Test new combined flow
    print("\n\n")
    asyncio.run(test_combined_research())
