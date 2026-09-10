"""Unit tests for activity data structures and business logic using AAA pattern.

Tests the core logic of activities, participants, and validation rules.
Each test follows AAA:
  - Arrange: Set up test data structures
  - Act: Execute logic being tested
  - Assert: Verify expected outcomes
"""

import pytest


class TestActivityDataStructure:
    """Tests for activity data structure and properties."""

    def test_activity_has_required_fields(self, client):
        """
        Arrange: Fetch activities from API
        Act: Get an activity
        Assert: Activity contains required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert - each activity must have these fields
        for activity_name, activity in activities.items():
            assert "description" in activity, f"{activity_name} missing description"
            assert "participants" in activity, f"{activity_name} missing participants"
            assert isinstance(activity["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_activity_description_is_string(self, client):
        """
        Arrange: Fetch all activities
        Act: Check description type
        Assert: All descriptions are non-empty strings
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity in activities.items():
            assert isinstance(activity["description"], str)
            assert len(activity["description"]) > 0

    def test_participants_list_is_list_of_strings(self, client):
        """
        Arrange: Fetch activities
        Act: Examine participants lists
        Assert: Participants are list of email strings
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity in activities.items():
            assert isinstance(activity["participants"], list)
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestParticipantManagement:
    """Tests for adding and removing participants."""

    def test_signup_increases_participant_count(self, client):
        """
        Arrange: Get current participant count for Chess Club
        Act: Sign up a new student
        Assert: Participant count increases by 1
        """
        # Arrange
        activity_name = "Chess Club"
        email = "participant@test.com"

        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert signup_response.status_code == 200
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1

    def test_unregister_decreases_participant_count(self, client):
        """
        Arrange: Get current participant count for Programming Class (has 2 pre-enrolled)
        Act: Unregister one participant
        Assert: Participant count decreases by 1
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert unregister_response.status_code == 200
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1

    def test_participant_email_unique_per_activity(self, client):
        """
        Arrange: Sign up student for activity
        Act: Attempt to sign up same student again
        Assert: Duplicate signup rejected
        """
        # Arrange
        activity_name = "Robotics Team"
        email = "unique_student@test.com"

        # First signup should succeed
        first_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert first_signup.status_code == 200

        # Act - attempt duplicate
        duplicate_signup = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert duplicate_signup.status_code == 400
        assert "already signed up" in duplicate_signup.json()["detail"]


class TestActivityValidation:
    """Tests for activity validation and error handling."""

    def test_invalid_activity_name_returns_404(self, client):
        """
        Arrange: Invalid activity name
        Act: Try to access non-existent activity
        Assert: Returns 404 Not Found
        """
        # Arrange
        invalid_names = [
            "Swimming Pool Club",
            "Chess League",
            "Invalid Activity 123",
            ""
        ]

        # Act & Assert
        for invalid_name in invalid_names:
            if invalid_name:  # Skip empty string for signup
                response = client.post(f"/activities/{invalid_name}/signup?email=test@test.com")
                assert response.status_code == 404

    def test_empty_email_parameter(self, client):
        """
        Arrange: Valid activity but empty email
        Act: Try to signup with empty email
        Assert: Request completes (FastAPI may accept empty string)
        """
        # Arrange
        activity_name = "Chess Club"
        email = ""

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - FastAPI will accept empty email, but we can verify response
        # The behavior depends on implementation, but should not crash
        assert response.status_code in [200, 400]

    def test_activity_name_case_sensitive(self, client):
        """
        Arrange: Activity names with different cases
        Act: Try to access with wrong case
        Assert: Should fail (case-sensitive matching)
        """
        # Arrange
        correct_name = "Chess Club"
        wrong_case_name = "chess club"
        email = "test@test.com"

        # Act & Assert
        wrong_response = client.post(f"/activities/{wrong_case_name}/signup?email={email}")
        assert wrong_response.status_code == 404


class TestActivityCounts:
    """Tests for participant count tracking and max capacity."""

    def test_max_participants_field_present(self, client):
        """
        Arrange: Fetch activities
        Act: Check for max_participants field
        Assert: Activities with max_participants defined have the field
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert - some activities have max_participants defined
        activities_with_max = [
            activity for activity in activities.values()
            if "max_participants" in activity
        ]
        assert len(activities_with_max) > 0

    def test_participants_not_exceed_returned_data(self, client):
        """
        Arrange: Get all activities
        Act: Count participants
        Assert: Participant counts are reasonable (< 100 for test data)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity in activities.items():
            participant_count = len(activity["participants"])
            assert participant_count < 100  # Sanity check for test data

    def test_activity_state_persists_between_calls(self, client):
        """
        Arrange: Sign up a student
        Act: Query activities twice
        Assert: Student appears in both queries (state persists)
        """
        # Arrange
        activity_name = "Drama Club"
        email = "persistent_student@test.com"

        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200

        # Act - query twice
        first_query = client.get("/activities")
        second_query = client.get("/activities")

        # Assert
        assert email in first_query.json()[activity_name]["participants"]
        assert email in second_query.json()[activity_name]["participants"]
