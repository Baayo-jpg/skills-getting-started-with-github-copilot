import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Prepare the test client
        Act: Send GET request to /activities
        Assert: Verify response contains all activities with correct structure
        """
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) > 0
        assert "Chess Club" in activities_data
        assert all(key in activities_data["Chess Club"] for key in expected_keys)

    def test_get_activities_contains_participants(self, client, reset_activities):
        """
        Arrange: Prepare the test client
        Act: Send GET request to /activities
        Assert: Verify participants list is present for each activity
        """
        # Arrange (implicit)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Prepare test data with new email not yet signed up
        Act: Send POST request to signup endpoint
        Assert: Verify student is successfully signed up
        """
        # Arrange
        activity_name = sample_activity
        email = sample_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_duplicate_email_fails(self, client, reset_activities, sample_activity):
        """
        Arrange: Sign up a student first, then attempt to sign up again
        Act: Send POST request with same email
        Assert: Verify request fails with 400 status and appropriate error message
        """
        # Arrange
        activity_name = sample_activity
        email = "michael@mergington.edu"  # Already signed up for Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_invalid_activity_fails(self, client, reset_activities, sample_email):
        """
        Arrange: Prepare invalid activity name
        Act: Send POST request with non-existent activity
        Assert: Verify request fails with 404 status
        """
        # Arrange
        activity_name = "Non-Existent Activity"
        email = sample_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_adds_participant_to_activity(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Prepare test data
        Act: Sign up a student and then retrieve activities
        Assert: Verify participant appears in activity's participant list
        """
        # Arrange
        activity_name = sample_activity
        email = sample_email

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, reset_activities, sample_activity):
        """
        Arrange: Use a student already signed up for an activity
        Act: Send DELETE request to unregister endpoint
        Assert: Verify student is successfully unregistered
        """
        # Arrange
        activity_name = sample_activity
        email = "michael@mergington.edu"  # Already signed up for Chess Club

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_removes_participant_from_activity(self, client, reset_activities, sample_activity):
        """
        Arrange: Use a student already signed up
        Act: Unregister the student and retrieve activities
        Assert: Verify participant is no longer in activity's participant list
        """
        # Arrange
        activity_name = sample_activity
        email = "michael@mergington.edu"

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert unregister_response.status_code == 200
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_not_signed_up_fails(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Use an email not signed up for the activity
        Act: Send DELETE request to unregister endpoint
        Assert: Verify request fails with 400 status
        """
        # Arrange
        activity_name = sample_activity
        email = sample_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_unregister_invalid_activity_fails(self, client, reset_activities, sample_email):
        """
        Arrange: Prepare invalid activity name
        Act: Send DELETE request with non-existent activity
        Assert: Verify request fails with 404 status
        """
        # Arrange
        activity_name = "Non-Existent Activity"
        email = sample_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_then_signup_again_succeeds(self, client, reset_activities, sample_activity):
        """
        Arrange: Unregister a student from an activity
        Act: Sign the same student up again
        Assert: Verify student can re-sign up after unregistering
        """
        # Arrange
        activity_name = sample_activity
        email = "michael@mergington.edu"

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
