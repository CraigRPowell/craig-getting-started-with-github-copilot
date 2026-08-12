"""
Integration tests for the Mergington High School Activities API.

Tests cover all endpoints using FastAPI's TestClient and follow the
Arrange-Act-Assert (AAA) pattern for clear test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """
        Test that GET /activities returns all activities with 200 status.
        
        Arrange: No setup needed (using fixture data)
        Act: Call GET /activities
        Assert: Status is 200 and response contains activities
        """
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200, "Expected 200 OK response"
        activities = response.json()
        assert isinstance(activities, dict), "Response should be a dictionary of activities"
        assert len(activities) == expected_activity_count, f"Expected {expected_activity_count} activities"

    def test_get_activities_response_structure(self, client):
        """
        Test that activity objects have required fields.
        
        Arrange: No setup needed
        Act: Call GET /activities and inspect first activity
        Assert: Activity contains all required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        first_activity = next(iter(activities.values()))
        assert all(field in first_activity for field in required_fields), \
            f"Activity missing required fields. Expected: {required_fields}"

    def test_get_activities_participants_is_list(self, client):
        """
        Test that participants field is a list of emails.
        
        Arrange: No setup needed
        Act: Call GET /activities
        Assert: Participants field is a list
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name}: participants should be a list"
            for participant in activity_data["participants"]:
                assert isinstance(participant, str), \
                    f"{activity_name}: participant should be a string (email)"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_adds_participant(self, client):
        """
        Test that a new participant can sign up for an activity.
        
        Arrange: Prepare activity name and new participant email
        Act: Send POST request to signup endpoint
        Assert: Participant is added and response confirms success
        """
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_participants = 2  # Chess Club starts with 2 participants

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200, "Expected 200 OK for successful signup"
        result = response.json()
        assert "message" in result, "Response should contain a message"
        assert new_email in result["message"], "Message should mention the email"

        # Verify participant was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity]["participants"], \
            "New participant should be in activity's participants list"
        assert len(activities[activity]["participants"]) == initial_participants + 1, \
            "Participants count should increase by 1"

    def test_signup_duplicate_returns_400(self, client):
        """
        Test that duplicate signup is rejected with 400 error.
        
        Arrange: Pick an email already signed up for an activity
        Act: Send signup request with existing participant email
        Assert: Returns 400 status and error message
        """
        # Arrange
        activity = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400, "Expected 400 Bad Request for duplicate signup"
        result = response.json()
        assert "detail" in result, "Response should contain error detail"
        assert "already signed up" in result["detail"].lower(), \
            "Error message should mention duplicate signup"

    def test_signup_invalid_activity_returns_404(self, client):
        """
        Test that signup for non-existent activity returns 404.
        
        Arrange: Use non-existent activity name
        Act: Send signup request for invalid activity
        Assert: Returns 404 status and error message
        """
        # Arrange
        invalid_activity = "Non-existent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404, "Expected 404 Not Found for invalid activity"
        result = response.json()
        assert "detail" in result, "Response should contain error detail"
        assert "not found" in result["detail"].lower(), \
            "Error message should indicate activity not found"

    def test_signup_participant_appears_in_activities_list(self, client):
        """
        Test that new participant appears in GET /activities.
        
        Arrange: Prepare new email and activity
        Act: Sign up participant, then retrieve activities
        Assert: Participant appears in the activity's participants list
        """
        # Arrange
        activity = "Soccer Club"
        new_email = "newsoccer@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200, "Signup should succeed"
        activities = activities_response.json()
        assert new_email in activities[activity]["participants"], \
            "New participant should appear in activities list"


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_delete_participant_removes_from_activity(self, client):
        """
        Test that deleting a participant removes them from activity.
        
        Arrange: Get initial participant count
        Act: Send DELETE request for an existing participant
        Assert: Participant is removed and count decreases
        """
        # Arrange
        activity = "Robotics Club"
        email_to_remove = "noah@mergington.edu"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity]["participants"]
        initial_count = len(initial_participants)

        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )

        # Assert
        assert response.status_code == 200, "Expected 200 OK for successful deletion"
        result = response.json()
        assert "message" in result, "Response should contain a message"

        # Verify participant was actually removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity]["participants"]
        assert email_to_remove not in updated_participants, \
            "Removed participant should not be in participants list"
        assert len(updated_participants) == initial_count - 1, \
            "Participants count should decrease by 1"

    def test_delete_nonexistent_participant_returns_404(self, client):
        """
        Test that deleting a non-existent participant returns 404.
        
        Arrange: Use email not in activity
        Act: Send DELETE request for non-existent participant
        Assert: Returns 404 status and error message
        """
        # Arrange
        activity = "Chess Club"
        email_not_in_activity = "nothere@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email_not_in_activity}"
        )

        # Assert
        assert response.status_code == 404, "Expected 404 Not Found for non-existent participant"
        result = response.json()
        assert "detail" in result, "Response should contain error detail"
        assert "not found" in result["detail"].lower(), \
            "Error message should indicate participant not found"

    def test_delete_from_invalid_activity_returns_404(self, client):
        """
        Test that deleting from non-existent activity returns 404.
        
        Arrange: Use invalid activity name
        Act: Send DELETE request with invalid activity
        Assert: Returns 404 status and error message
        """
        # Arrange
        invalid_activity = "Non-existent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404, "Expected 404 Not Found for invalid activity"
        result = response.json()
        assert "detail" in result, "Response should contain error detail"
        assert "not found" in result["detail"].lower(), \
            "Error message should indicate activity not found"

    def test_delete_multiple_participants_works_independently(self, client):
        """
        Test that deleting one participant doesn't affect others.
        
        Arrange: Identify multiple participants in an activity
        Act: Delete one participant
        Assert: Other participants remain and count is correct
        """
        # Arrange
        activity = "Robotics Club"
        all_participants = ["noah@mergington.edu", "ava@mergington.edu", "ethan@mergington.edu"]
        email_to_remove = "noah@mergington.edu"
        other_emails = [e for e in all_participants if e != email_to_remove]

        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )

        # Assert
        assert response.status_code == 200, "Deletion should succeed"
        
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        
        assert email_to_remove not in participants, "Removed email should not be in list"
        for other_email in other_emails:
            assert other_email in participants, f"{other_email} should still be in list"
        assert len(participants) == len(all_participants) - 1, "Count should be one less"


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        Arrange: No setup needed
        Act: Send GET request to root path (following redirects)
        Assert: Final URL should be /static/index.html
        """
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [307, 308], \
            "Root should return a redirect status code (307 or 308)"
        assert "location" in response.headers, "Redirect should include Location header"
        assert "static/index.html" in response.headers["location"], \
            "Redirect should point to /static/index.html"
