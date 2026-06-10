import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Fixture that provides a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture that resets activities to initial state before each test"""
    original_activities = copy.deepcopy(activities)
    yield
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_email():
    """Fixture that provides a sample email for testing"""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity():
    """Fixture that provides a sample activity name"""
    return "Chess Club"
