"""
Tests for the Mergington High School API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_with_test_data(self, client, mock_activities_with_test_data):
        """Test GET /activities with controlled test data."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Test Activity" in data
        assert "Empty Activity" in data
        
        # Check Test Activity
        test_activity = data["Test Activity"]
        assert test_activity["description"] == "A test activity"
        assert test_activity["max_participants"] == 5
        assert len(test_activity["participants"]) == 2
        assert "test1@mergington.edu" in test_activity["participants"]
        
        # Check Empty Activity
        empty_activity = data["Empty Activity"]
        assert empty_activity["max_participants"] == 10
        assert len(empty_activity["participants"]) == 0


class TestSignupEndpoint:
    """Test the signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client, mock_activities_with_test_data):
        """Test successful signup for an existing activity."""
        email = "newstudent@mergington.edu"
        activity_name = "Empty Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client):
        """Test signup for non-existent activity returns 404."""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant_fails(self, client, mock_activities_with_test_data):
        """Test that signing up the same participant twice fails."""
        email = "test1@mergington.edu"  # Already in Test Activity
        activity_name = "Test Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_signup_with_encoded_activity_name(self, client, mock_activities_with_test_data):
        """Test signup with URL-encoded activity name."""
        email = "newstudent@mergington.edu"
        activity_name = "Test Activity"  # Contains space
        encoded_activity_name = "Test%20Activity"
        
        response = client.post(f"/activities/{encoded_activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
    
    def test_signup_with_encoded_email(self, client, mock_activities_with_test_data):
        """Test signup with URL-encoded email."""
        email = "new.student+test@mergington.edu"
        encoded_email = "new.student%2Btest%40mergington.edu"
        activity_name = "Empty Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"


class TestUnregisterEndpoint:
    """Test the unregister endpoint."""
    
    def test_unregister_existing_participant_success(self, client, mock_activities_with_test_data):
        """Test successful unregistration of an existing participant."""
        email = "test1@mergington.edu"  # Exists in Test Activity
        activity_name = "Test Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test unregister from non-existent activity returns 404."""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_non_participant_fails(self, client, mock_activities_with_test_data):
        """Test unregistering a non-participant fails."""
        email = "notregistered@mergington.edu"
        activity_name = "Test Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
    
    def test_unregister_with_encoded_names(self, client, mock_activities_with_test_data):
        """Test unregister with URL-encoded activity name and email."""
        email = "test2@mergington.edu"
        activity_name = "Test Activity"
        encoded_activity_name = "Test%20Activity"
        encoded_email = "test2%40mergington.edu"
        
        response = client.delete(f"/activities/{encoded_activity_name}/unregister?email={encoded_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple operations."""
    
    def test_signup_then_unregister_workflow(self, client, mock_activities_with_test_data):
        """Test the complete workflow of signing up and then unregistering."""
        email = "workflow@mergington.edu"
        activity_name = "Empty Activity"
        
        # Initial state - verify participant is not in activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
        initial_count = len(activities_data[activity_name]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        assert len(activities_data[activity_name]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
        assert len(activities_data[activity_name]["participants"]) == initial_count
    
    def test_multiple_participants_same_activity(self, client, mock_activities_with_test_data):
        """Test adding multiple participants to the same activity."""
        activity_name = "Empty Activity"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Get initial state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        initial_count = len(activities_data[activity_name]["participants"])
        
        # Sign up all participants
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data[activity_name]["participants"]
        
        assert len(participants) == initial_count + len(emails)
        for email in emails:
            assert email in participants
    
    def test_activity_capacity_management(self, client, mock_activities_with_test_data):
        """Test that activities properly track participant counts vs capacity."""
        # Use Test Activity which has max_participants: 5 and currently has 2 participants
        activity_name = "Test Activity"
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        activity = activities_data[activity_name]
        
        current_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        available_spots = max_participants - current_count
        
        assert current_count == 2
        assert max_participants == 5
        assert available_spots == 3
        
        # Add participants up to the limit (we can add 3 more)
        new_emails = [f"student{i}@mergington.edu" for i in range(available_spots)]
        
        for email in new_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify we're now at capacity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        final_participants = activities_data[activity_name]["participants"]
        
        assert len(final_participants) == max_participants
        for email in new_emails:
            assert email in final_participants