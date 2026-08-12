"""
Pytest configuration and fixtures for the FastAPI application tests.

This module provides:
- TestClient instance for testing endpoints
- Fresh test data (activities) per test
- Monkeypatching of app.activities for test isolation
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def test_activities():
    """
    Provide a fresh copy of test activities data.
    
    Each test gets an isolated copy to prevent cross-test pollution.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
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
        "Basketball Team": {
            "description": "Competitive basketball team and practice sessions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "james@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Recreational and competitive soccer for all skill levels",
            "schedule": "Tuesdays and Saturdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances, acting, and stage production",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competition",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu"]
        }
    }


@pytest.fixture
def client(test_activities, monkeypatch):
    """
    Provide a TestClient with isolated test data.
    
    Uses monkeypatch to replace app.activities with test data for each test.
    This ensures tests don't interfere with each other.
    """
    monkeypatch.setattr("src.app.activities", test_activities)
    return TestClient(app)
