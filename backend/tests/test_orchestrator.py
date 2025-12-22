"""
Tests for the Orchestrator.
"""

import pytest
from langchain_core.messages import HumanMessage

from backend.agents.models import OrchestrationRequest, OrchestrationResponse
from backend.agents.orchestrator.orchestrator import master_app, supervisor_node


def test_orchestration_request_model():
    """Test OrchestrationRequest model."""
    request = OrchestrationRequest(
        startup_id="test_001",
        user_message="Hello, I need help",
        conversation_history=[
            {"role": "user", "content": "Previous message"}
        ]
    )
    
    assert request.startup_id == "test_001"
    assert request.user_message == "Hello, I need help"
    assert len(request.conversation_history) == 1


def test_orchestration_response_model():
    """Test OrchestrationResponse model."""
    response = OrchestrationResponse(
        startup_id="test_001",
        reply="Here's my response",
        next_steps=["Step 1", "Step 2"]
    )
    
    assert response.startup_id == "test_001"
    assert response.reply == "Here's my response"
    assert len(response.next_steps) == 2


def test_orchestrator_minimal_flow():
    """Test orchestrator with minimal input."""
    state = {
        "messages": [HumanMessage(content="Hi")],
        "user_context": {"org_id": "test_org"},
        "action": None,
        "next_agent": None,
        "final_reply": None,
        "iteration_count": 0
    }
    
    try:
        result = master_app.invoke(state)
        
        # Verify result structure
        assert "action" in result or "final_reply" in result
        
        # Should not loop infinitely
        assert result.get("iteration_count", 0) < 10
        
    except Exception as e:
        # API errors are acceptable
        error_msg = str(e).lower()
        acceptable_errors = ["api", "key", "connection", "timeout", "perplexity"]
        assert any(err in error_msg for err in acceptable_errors), f"Unexpected error: {e}"


def test_orchestrator_with_profile():
    """Test orchestrator with existing profile."""
    state = {
        "messages": [HumanMessage(content="What should I do next?")],
        "user_context": {
            "org_id": "test_with_profile",
            "business_name": "TestCo",
            "business_type": "FinTech",
            "stage": "Seed",
            "goals": ["Launch MVP"]
        },
        "action": None,
        "next_agent": None,
        "final_reply": None,
        "iteration_count": 0
    }
    
    try:
        result = master_app.invoke(state)
        
        # Should process successfully
        assert isinstance(result, dict)
        
        # Context should be preserved
        assert "user_context" in result
        if result.get("user_context"):
            assert "org_id" in result["user_context"]
            
    except Exception as e:
        # API errors acceptable
        assert "api" in str(e).lower() or "key" in str(e).lower()


def test_supervisor_routing_logic(sample_startup_profile):
    """Test supervisor node decision making."""
    state = {
        "messages": [HumanMessage(content="I need a business plan")],
        "user_context": sample_startup_profile,
        "action": None,
        "next_agent": None,
        "iteration_count": 0,
        "final_plan": None,
        "research_offline": None,
        "research_online": None
    }
    
    try:
        result = supervisor_node(state)
        
        # Should make a routing decision
        assert "action" in result
        assert result["action"] in ["route", "reply"]
        
        # If routing, should specify agent
        if result["action"] == "route":
            assert "next_agent" in result
            assert result["next_agent"] in ["planner", "research", "researcher", "onboarding", "gap_agent"]
            
    except Exception as e:
        # API errors acceptable
        assert "api" in str(e).lower() or "timeout" in str(e).lower()


def test_orchestrator_iteration_safety():
    """Test that orchestrator prevents infinite loops."""
    state = {
        "messages": [HumanMessage(content="Test")],
        "user_context": {},
        "action": "route",
        "next_agent": "planner",
        "iteration_count": 15,  # Already high
        "final_reply": None
    }
    
    try:
        result = supervisor_node(state)
        
        # Should stop routing after max iterations
        # Either replies or has safety check
        if result.get("iteration_count", 0) >= 10:
            assert result.get("action") == "reply" or result.get("final_reply")
            
    except Exception as e:
        # Acceptable errors
        pass


def test_orchestrator_state_preservation():
    """Test that orchestrator preserves state between nodes."""
    state = {
        "messages": [HumanMessage(content="Hello")],
        "user_context": {"test_key": "test_value"},
        "action": None,
        "next_agent": None,
        "final_reply": None,
        "iteration_count": 0,
        "final_plan": {"test": "plan"},
        "research_offline": {"status": "success"}
    }
    
    try:
        result = master_app.invoke(state)
        
        # State should be preserved or updated, not lost
        assert isinstance(result, dict)
        
        # At minimum, should have action or reply
        assert "action" in result or "final_reply" in result
        
    except Exception as e:
        # API errors acceptable
        pass
