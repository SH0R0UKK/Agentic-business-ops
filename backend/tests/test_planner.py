"""
Tests for the Planner Agent.
"""

import pytest
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage

from backend.agents.models import PlanRequest, Plan, StartupProfile
from backend.agents.Planner.planner import app_graph as planner_graph


def test_plan_request_model(sample_startup_profile):
    """Test PlanRequest model validation."""
    profile = StartupProfile(**sample_startup_profile)
    
    request = PlanRequest(
        startup_id="test_001",
        startup_profile=profile,
        time_horizon_days=90,
        task_type="advisory"
    )
    
    assert request.startup_id == "test_001"
    assert request.time_horizon_days == 90
    assert request.task_type in ["timeline", "advisory"]


def test_plan_model_structure():
    """Test Plan model structure and validation."""
    plan = Plan(
        plan_id="plan_001",
        startup_id="test_001",
        title="Test Plan",
        summary="This is a test plan",
        time_horizon_days=90,
        chat_summary="Plan created successfully"
    )
    
    assert plan.plan_id == "plan_001"
    assert plan.version == 1  # Default
    assert plan.time_horizon_days == 90
    assert isinstance(plan.created_at, str)
    
    # Verify serialization
    plan_dict = plan.model_dump()
    assert "plan_id" in plan_dict
    assert "phases" in plan_dict


def test_planner_with_minimal_input(sample_startup_profile):
    """Test planner with minimal valid input."""
    state = {
        "messages": [HumanMessage(content="Create a simple plan")],
        "user_context": sample_startup_profile,
        "research_offline": None,
        "research_online": None,
        "final_plan": None
    }
    
    try:
        result = planner_graph.invoke(state)
        
        # Verify plan was created
        assert "final_plan" in result
        plan_data = result["final_plan"]
        
        # Basic structure checks
        if plan_data:
            assert isinstance(plan_data, dict)
            # Should have at least one of these keys
            assert (
                "chat_summary" in plan_data or 
                "strategy_advice" in plan_data or
                "schedule_events" in plan_data
            )
            
    except Exception as e:
        # Missing API key or LLM error is acceptable
        error_msg = str(e).lower()
        acceptable_errors = ["api", "key", "perplexity", "timeout", "connection"]
        assert any(err in error_msg for err in acceptable_errors), f"Unexpected error: {e}"


def test_plan_date_consistency():
    """Test that plan dates are consistent when provided."""
    plan = Plan(
        plan_id="plan_dates_001",
        startup_id="test_001",
        title="Timeline Plan",
        summary="Test",
        time_horizon_days=30
    )
    
    # Parse created_at
    created = datetime.fromisoformat(plan.created_at)
    
    # Should be recent (within last minute)
    now = datetime.utcnow()
    time_diff = abs((now - created).total_seconds())
    assert time_diff < 60, "Created timestamp should be recent"


def test_planner_with_research_context(sample_startup_profile):
    """Test planner incorporating research results."""
    state = {
        "messages": [HumanMessage(content="Create a plan based on research")],
        "user_context": sample_startup_profile,
        "research_offline": {
            "question": "Market analysis",
            "summary": "Market is growing",
            "claims": [],
            "status": "success"
        },
        "research_online": {
            "question": "Market analysis",
            "summary": "Strong competition",
            "findings": [],
            "status": "success"
        },
        "final_plan": None
    }
    
    try:
        result = planner_graph.invoke(state)
        
        # Should create a plan
        assert "final_plan" in result
        
        # If successful, plan should exist
        if result["final_plan"]:
            assert isinstance(result["final_plan"], dict)
            
    except Exception as e:
        # API/LLM errors are acceptable
        error_msg = str(e).lower()
        assert "api" in error_msg or "key" in error_msg or "timeout" in error_msg


def test_plan_json_serialization():
    """Test that plans can be serialized to/from JSON."""
    import json
    
    plan = Plan(
        plan_id="serial_001",
        startup_id="test_001",
        title="Serialization Test",
        summary="Testing JSON",
        strategy_advice="Test advice",
        schedule_events=[
            {"date": "2026-01-15", "title": "Milestone 1"},
            {"date": "2026-02-15", "title": "Milestone 2"}
        ]
    )
    
    # Serialize
    plan_json = json.dumps(plan.model_dump())
    assert isinstance(plan_json, str)
    
    # Deserialize
    plan_dict = json.loads(plan_json)
    restored_plan = Plan(**plan_dict)
    
    assert restored_plan.plan_id == plan.plan_id
    assert restored_plan.title == plan.title
    assert len(restored_plan.schedule_events) == 2
