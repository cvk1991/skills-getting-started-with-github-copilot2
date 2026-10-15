import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    # Arrange
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Art Club": {
                "description": "Explore visual art",
                "schedule": "Wednesdays",
                "max_participants": 16,
                "participants": ["alice@example.com"],
            }
        },
    )

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_and_participants(client):
    # Arrange
    expected_participants = ["alice@example.com"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Art Club"]["participants"] == expected_participants


def test_signup_adds_participant_to_activity(client):
    # Arrange
    email = "bob@example.com"

    # Act
    signup_response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json() == {"message": "Signed up bob@example.com for Art Club"}
    assert email in activities_response.json()["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "alice@example.com"

    # Act
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    email = "bob@example.com"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    email = "alice@example.com"

    # Act
    response = client.delete(f"/activities/Art%20Club/participants/{email}")
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Removed alice@example.com from Art Club"}
    assert email not in activities_response.json()["Art Club"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    email = "alice@example.com"

    # Act
    response = client.delete(f"/activities/Unknown%20Club/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    email = "bob@example.com"

    # Act
    response = client.delete(f"/activities/Art%20Club/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"