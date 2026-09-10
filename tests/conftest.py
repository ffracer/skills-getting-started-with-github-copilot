"""Test configuration and fixtures for the Activity Management API tests.

Provides reusable fixtures and setup/teardown logic for testing.
Uses AAA (Arrange-Act-Assert) pattern conventions.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


# Store the initial state of activities for reset between tests
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "A club for students who enjoy playing chess.",
        "participants": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Robotics Team": {
        "description": "A team that builds and programs robots for competitions.",
        "participants": []
    },
    "Drama Club": {
        "description": "A club for students interested in acting and theater production.",
        "participants": []
    }
}


@pytest.fixture(scope="function", autouse=True)
def reset_app_state():
    """
    Fixture: Reset app state before each test.
    
    Resets the shared in-memory activities dictionary to its initial state
    to provide test isolation. Runs automatically before each test.
    
    This ensures that modifications made by one test (e.g., removing a
    participant) don't affect subsequent tests.
    """
    from src import app as app_module
    # Reset activities to initial state
    app_module.activities.clear()
    app_module.activities.update({
        name: {
            "description": data["description"],
            "participants": data["participants"].copy()
        }
        for name, data in INITIAL_ACTIVITIES.items()
    })
    # Add optional fields that some activities have
    if "Programming Class" in app_module.activities:
        app_module.activities["Programming Class"]["schedule"] = INITIAL_ACTIVITIES["Programming Class"]["schedule"]
        app_module.activities["Programming Class"]["max_participants"] = INITIAL_ACTIVITIES["Programming Class"]["max_participants"]
    if "Gym Class" in app_module.activities:
        app_module.activities["Gym Class"]["schedule"] = INITIAL_ACTIVITIES["Gym Class"]["schedule"]
        app_module.activities["Gym Class"]["max_participants"] = INITIAL_ACTIVITIES["Gym Class"]["max_participants"]
    yield


@pytest.fixture(scope="function")
def client():
    """
    Fixture: TestClient instance for making HTTP requests to the app.
    
    Function-scoped (after reset_app_state fixture) to provide test isolation.
    Each test receives a fresh client with reset in-memory data.
    
    Yields:
        TestClient: Configured test client for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def sample_email():
    """
    Fixture: Sample student email for signup tests.
    
    Function-scoped so each test gets a fresh email to avoid conflicts
    with duplicate signup tests.
    
    Yields:
        str: A test student email address.
    """
    return "test_student@mergington.edu"


@pytest.fixture(scope="function")
def sample_activities():
    """
    Fixture: Expected activity names in the API.
    
    Returns a list of all activity names that should exist in the system.
    Used for parameterized tests and validation.
    
    Yields:
        list: Activity names available in the system.
    """
    return [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Robotics Team",
        "Drama Club"
    ]


@pytest.fixture(scope="function")
def preset_participants():
    """
    Fixture: Participants preset in certain activities at startup.
    
    Some activities come with pre-populated participants from app.py.
    This fixture maps which activities have which participants.
    
    Yields:
        dict: Mapping of activity names to list of pre-enrolled participants.
    """
    return {
        "Chess Club": [],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
        "Robotics Team": [],
        "Drama Club": []
    }
