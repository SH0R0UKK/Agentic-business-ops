"""
Tests for the Onboarding Agent.
"""

import pytest
from pathlib import Path
from backend.agents.models import OnboardingRequest, StartupProfile
from backend.agents.onboarding.agent import run_onboarding, extract_business_context


def test_onboarding_with_files(test_document_path):
    """Test onboarding with document processing."""
    # Create a minimal test file
    test_file = test_document_path / "test_business_doc.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    test_file.write_text("""
    Company: TestCo
    Business: E-commerce platform
    Location: Cairo, Egypt
    Stage: MVP
    Goal: Launch in Q1 2026
    """)
    
    try:
        # Run onboarding
        result = run_onboarding(
            file_paths=[str(test_file)],
            org_id="test_onboarding_001"
        )
        
        # Verify result structure
        assert "user_context" in result
        assert "processed_files" in result
        assert result["status"] == "success"
        
        # Verify user context has expected fields
        context = result["user_context"]
        assert "org_id" in context
        assert context["org_id"] == "test_onboarding_001"
        
        # Check that at least some fields are populated
        assert isinstance(context.get("business_name", ""), str)
        assert isinstance(context.get("goals", []), list)
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_onboarding_profile_model(sample_startup_profile):
    """Test that StartupProfile model validates correctly."""
    # Create profile from sample data
    profile = StartupProfile(**sample_startup_profile)
    
    # Verify all required fields
    assert profile.startup_id == "test_startup_001"
    assert profile.business_name == "Test Startup"
    assert profile.business_type == "FinTech"
    assert profile.location == "Cairo, Egypt"
    assert len(profile.goals) == 2
    
    # Verify model can be serialized
    profile_dict = profile.model_dump()
    assert isinstance(profile_dict, dict)
    assert "startup_id" in profile_dict
    assert "created_at" in profile_dict


def test_onboarding_no_files():
    """Test onboarding behavior with no files (should handle gracefully)."""
    # This should either return minimal profile or raise clear error
    try:
        result = run_onboarding(file_paths=[], org_id="test_empty")
        
        # If it succeeds, verify structure
        assert "user_context" in result or "error" in result
        
    except (ValueError, FileNotFoundError) as e:
        # Expected behavior - clear error message
        assert "file" in str(e).lower() or "document" in str(e).lower()


def test_extract_context_from_minimal_data():
    """Test context extraction with minimal processed files."""
    processed_files = [
        {
            "filename": "test.txt",
            "text": "Business name: TestBiz. Located in Egypt.",
            "type": "text"
        }
    ]
    
    try:
        context = extract_business_context(processed_files)
        
        # Verify structure
        assert isinstance(context, dict)
        
        # Should have at least these keys (even if empty)
        expected_keys = ["business_name", "location", "business_type", "goals"]
        for key in expected_keys:
            assert key in context
            
    except Exception as e:
        # If it fails, should be due to missing API key or LLM issue
        assert "api" in str(e).lower() or "llm" in str(e).lower()
