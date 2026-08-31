"""
Tests for activity management endpoints.

Tests cover:
- GET /activities: Retrieving all activities with their details
- POST /activities/{activity_name}/signup: Registering students for activities
- DELETE /activities/{activity_name}/unregister: Removing students from activities
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_all_activities_returns_list(self, test_client):
        """Verify that GET /activities returns all 9 activities."""
        response = test_client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9

    def test_activities_have_required_keys(self, test_client):
        """Verify each activity contains all required fields."""
        response = test_client.get("/activities")
        activities = response.json()
        
        required_keys = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert activity_data.keys() == required_keys, \
                f"Activity '{activity_name}' missing required keys"

    def test_activities_data_types(self, test_client):
        """Verify data types of activity fields."""
        response = test_client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str), \
                f"'{activity_name}' description should be string"
            assert isinstance(activity_data["schedule"], str), \
                f"'{activity_name}' schedule should be string"
            assert isinstance(activity_data["max_participants"], int), \
                f"'{activity_name}' max_participants should be int"
            assert isinstance(activity_data["participants"], list), \
                f"'{activity_name}' participants should be list"

    def test_sample_participants_loaded(self, test_client):
        """Verify that sample participants are present in activities."""
        response = test_client.get("/activities")
        activities = response.json()
        
        # Chess Club should have michael and daniel
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Programming Class should have emma and sophia
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup(self, test_client):
        """Verify successful registration for an activity."""
        new_email = "new_student@mergington.edu"
        activity_name = "Chess Club"
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, test_client):
        """Verify that signup actually adds the participant to the activity."""
        new_email = "new_student@mergington.edu"
        activity_name = "Programming Class"
        
        # Sign up
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Verify participant was added
        response = test_client.get("/activities")
        activities = response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_duplicate_signup_returns_error(self, test_client):
        """Verify that signing up twice returns a 400 error."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, test_client):
        """Verify that signing up for non-existent activity returns 404."""
        response = test_client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class"
    ])
    def test_signup_multiple_activities(self, test_client, activity_name):
        """Verify signup works for different activities."""
        email = f"test_{activity_name.replace(' ', '_')}@mergington.edu"
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200

    def test_signup_with_special_characters_in_email(self, test_client):
        """Verify signup accepts emails with special characters."""
        email = "student+tag@mergington.edu"
        activity_name = "Chess Club"
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200

    def test_signup_url_encoding_activity_name(self, test_client):
        """Verify signup works with URL-encoded activity names with spaces."""
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        
        # The space should be URL-encoded as %20
        response = test_client.post(
            f"/activities/Chess%20Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_successful_unregister(self, test_client):
        """Verify successful unregistration from an activity."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant_from_activity(self, test_client):
        """Verify that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Unregister
        test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = test_client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_error(self, test_client):
        """Verify unregistering a student not in the activity returns 400."""
        email = "not_registered@mergington.edu"
        activity_name = "Chess Club"
        
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, test_client):
        """Verify unregistering from non-existent activity returns 404."""
        response = test_client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_then_can_signup_again(self, test_client):
        """Verify that a student can sign up after unregistering."""
        email = "test_student@mergington.edu"
        activity_name = "Chess Club"
        
        # Sign up
        response1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Robotics Club"
    ])
    def test_unregister_multiple_activities(self, test_client, activity_name):
        """Verify unregister works for different activities."""
        email = f"test_{activity_name.replace(' ', '_')}@mergington.edu"
        
        # First sign up
        test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200

    def test_unregister_url_encoding_activity_name(self, test_client):
        """Verify unregister works with URL-encoded activity names with spaces."""
        email = "michael@mergington.edu"
        
        # The space should be URL-encoded as %20
        response = test_client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
