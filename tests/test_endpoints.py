"""Integration tests for API endpoints using AAA (Arrange-Act-Assert) pattern.

Tests all endpoints: GET /, GET /activities, POST signup, DELETE unregister.
Each test follows the AAA pattern:
  - Arrange: Set up test data and preconditions via fixtures
  - Act: Make HTTP request to endpoint
  - Assert: Verify response status, body, and side effects
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint (redirect to static files)."""

    def test_root_redirects_to_static(self, client):
        """
        Arrange: TestClient is ready to accept requests
        Act: Make GET request to root endpoint
        Assert: Response should redirect (308) to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")

    def test_root_with_follow_redirects(self, client):
        """
        Arrange: TestClient configured to follow redirects
        Act: Make GET request to root following redirects
        Assert: Should successfully resolve to static HTML (200)
        """
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        # HTML content should be served (contains common HTML tags)
        assert "<!DOCTYPE" in response.text or "<html" in response.text


class TestGetActivities:
    """Tests for GET /activities endpoint (retrieve all activities)."""

    def test_get_activities_returns_all_activities(self, client, sample_activities):
        """
        Arrange: Sample list of expected activities
        Act: Make GET request to /activities
        Assert: Response contains all 5 activities with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 5
        for activity_name in sample_activities:
            assert activity_name in activities

    def test_get_activities_structure(self, client):
        """
        Arrange: TestClient ready
        Act: Request all activities
        Assert: Each activity has required fields (description, participants, schedule, max_participants)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_with_preset_participants(self, client, preset_participants):
        """
        Arrange: Known pre-enrolled participants in activities
        Act: Request all activities
        Assert: Activities with pre-enrolled participants show correct data
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert - Programming Class has emma@mergington.edu and sophia@mergington.edu
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]

        # Gym Class has john@mergington.edu and olivia@mergington.edu
        assert "john@mergington.edu" in activities["Gym Class"]["participants"]
        assert "olivia@mergington.edu" in activities["Gym Class"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, sample_email):
        """
        Arrange: Valid activity name and new student email
        Act: POST signup request for an activity
        Assert: Response is 200, contains success message, participant added
        """
        # Arrange
        activity_name = "Chess Club"
        email = sample_email

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_email):
        """
        Arrange: Empty activity (Chess Club) and new email
        Act: Sign up for activity
        Assert: Participant appears in activity's participant list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@test.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - verify by fetching activities
        assert response.status_code == 200
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_duplicate_email_fails(self, client):
        """
        Arrange: Student already signed up for Programming Class
        Act: Attempt to sign up same email again
        Assert: Response is 400 (Bad Request) with duplicate error
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already enrolled

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, sample_email):
        """
        Arrange: Activity name that doesn't exist
        Act: Attempt to sign up for non-existent activity
        Assert: Response is 404 (Not Found) with error message
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = sample_email

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_multiple_students_same_activity(self, client):
        """
        Arrange: Empty activity and two different student emails
        Act: Sign up two different students for same activity
        Assert: Both students successfully added to participant list
        """
        # Arrange
        activity_name = "Robotics Team"
        email1 = "student1@test.com"
        email2 = "student2@test.com"

        # Act - first signup
        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        # Act - second signup
        response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify both in participant list
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_success(self, client):
        """
        Arrange: Student enrolled in Programming Class (preset data)
        Act: DELETE request to unregister student
        Assert: Response is 200, success message, participant removed
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Pre-enrolled

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """
        Arrange: Student enrolled in Gym Class
        Act: Unregister student
        Assert: Participant no longer in activity's participant list
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Pre-enrolled

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert - verify removal
        assert response.status_code == 200
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_unregister_not_enrolled_fails(self, client):
        """
        Arrange: Student NOT enrolled in Chess Club
        Act: Attempt to unregister non-enrolled student
        Assert: Response is 400 (Bad Request) with error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@test.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """
        Arrange: Activity that doesn't exist
        Act: Attempt to unregister from non-existent activity
        Assert: Response is 404 (Not Found)
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "student@test.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_then_unregister_roundtrip(self, client):
        """
        Arrange: Fresh student email and empty activity
        Act: Sign up, then unregister same student
        Assert: Both operations succeed, participant list reflects changes
        """
        # Arrange
        activity_name = "Drama Club"
        email = "drama_student@test.com"

        # Act - signup
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200

        # Verify in list
        activities_after_signup = client.get("/activities")
        assert email in activities_after_signup.json()[activity_name]["participants"]

        # Act - unregister
        unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        assert unregister_response.status_code == 200

        # Assert - verify removed
        activities_after_unregister = client.get("/activities")
        assert email not in activities_after_unregister.json()[activity_name]["participants"]
