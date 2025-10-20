"""
Test configuration and fixtures for the Mergington High School API tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide sample activities data for testing."""
    return {
        "Test Activity": {
            "description": "A test activity",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Tuesdays, 2:00 PM - 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test."""
    # Store original activities
    original_activities = activities.copy()
    
    yield
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def mock_activities_with_test_data(sample_activities):
    """Replace activities with test data for testing."""
    # Store original activities
    original_activities = activities.copy()
    
    # Replace with test data
    activities.clear()
    activities.update(sample_activities)
    
    yield activities
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)