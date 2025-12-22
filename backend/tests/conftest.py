"""
Shared test fixtures and configuration for backend tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["BACKEND_PORT"] = "8001"  # Use different port for tests


@pytest.fixture
def sample_startup_profile():
    """Sample startup profile for testing."""
    return {
        "startup_id": "test_startup_001",
        "business_name": "Test Startup",
        "business_type": "FinTech",
        "sector": "Digital Payments",
        "location": "Cairo, Egypt",
        "stage": "Seed",
        "goals": ["Launch MVP", "Acquire 1000 users"],
        "key_constraints": ["Limited budget", "Small team"],
        "target_audience": "Young professionals",
        "unique_value": "Fast, secure mobile payments"
    }


@pytest.fixture
def sample_research_question():
    """Sample research question."""
    return "What is the market size for digital payments in Egypt?"


@pytest.fixture
def test_document_path():
    """Path to test documents directory."""
    return Path(__file__).parent.parent / "data" / "test_documents"


@pytest.fixture
def cleanup_db():
    """Cleanup test database after tests."""
    yield
    # Add cleanup logic if needed
    pass
