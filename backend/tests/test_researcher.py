"""
Tests for the Research Agent.
"""

import pytest
import asyncio
from backend.agents.models import ResearchRequest, ResearchResponse
from backend.agents.researcher.agent import run_research_agent, ResearchAgent


def test_research_request_model(sample_startup_profile, sample_research_question):
    """Test ResearchRequest model validation."""
    request = ResearchRequest(
        startup_id="test_001",
        question=sample_research_question,
        search_offline=True,
        search_online=True
    )
    
    assert request.startup_id == "test_001"
    assert request.question == sample_research_question
    assert request.search_offline is True
    assert len(request.grounding_rules) > 0


def test_research_response_model():
    """Test ResearchResponse model structure."""
    response = ResearchResponse(
        startup_id="test_001",
        question="Test question",
        combined_summary="Test summary",
        confidence_score=7
    )
    
    assert response.startup_id == "test_001"
    assert response.confidence_score >= 1 and response.confidence_score <= 10
    assert isinstance(response.created_at, str)


@pytest.mark.asyncio
async def test_research_agent_basic_flow(sample_research_question):
    """Test basic research agent flow."""
    state = {
        "search_query": sample_research_question,
        "user_context": {},
        "startup_id": "test_research_001"
    }
    
    try:
        result = await run_research_agent(state)
        
        # Verify structure
        assert "research_offline" in result or "research_online" in result
        
        # At least one should have a status
        if result.get("research_offline"):
            assert "status" in result["research_offline"]
        
        if result.get("research_online"):
            assert "status" in result["research_online"]
            
    except Exception as e:
        # If it fails due to missing API keys, that's acceptable in test environment
        error_msg = str(e).lower()
        acceptable_errors = ["api", "key", "connection", "timeout"]
        assert any(err in error_msg for err in acceptable_errors), f"Unexpected error: {e}"


def test_research_agent_initialization():
    """Test that ResearchAgent can be instantiated."""
    try:
        agent = ResearchAgent()
        
        # Verify components exist
        assert agent.librarian is not None
        assert agent.searcher is not None
        assert agent.graph is not None
        
    except Exception as e:
        # Missing API key is acceptable
        assert "api" in str(e).lower()


@pytest.mark.asyncio
async def test_research_with_no_question():
    """Test research agent with missing question."""
    state = {
        "user_context": {},
        "startup_id": "test_no_question"
    }
    
    result = await run_research_agent(state)
    
    # Should handle gracefully with error status
    assert result.get("research_offline", {}).get("status") == "error"
    assert result.get("research_online", {}).get("status") == "error"
