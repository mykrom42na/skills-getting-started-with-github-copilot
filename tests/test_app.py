"""FastAPI integration tests for the extracurricular activities API."""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Ensure each test runs with the original in-memory database."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_initial_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_prevents_duplicates():
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_endpoint():
    activity = "Programming Class"
    email = activities[activity]["participants"][0]

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_remove_participant_handles_missing_email():
    activity = "Programming Class"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered for this activity"
