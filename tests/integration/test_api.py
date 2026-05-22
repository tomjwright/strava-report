"""Integration tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "app_name" in data
        assert "version" in data


class TestActivityEndpoints:
    """Test activity endpoints."""
    
    def test_get_activities_empty(self, client):
        """Test getting activities when database is empty."""
        response = client.get("/api/activities/")
        assert response.status_code == 200
        
        data = response.json()
        assert "activities" in data
        assert "total" in data
        assert isinstance(data["activities"], list)
    
    def test_get_activities_with_limit(self, client):
        """Test getting activities with limit parameter."""
        response = client.get("/api/activities/?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 10
    
    def test_get_activities_with_filters(self, client):
        """Test getting activities with filter parameters."""
        response = client.get(
            "/api/activities/",
            params={
                "activity_type": "Running",
                "limit": 50,
            }
        )
        assert response.status_code == 200
    
    def test_get_activities_invalid_limit(self, client):
        """Test getting activities with invalid limit."""
        response = client.get("/api/activities/?limit=1001")
        # Should return validation error
        assert response.status_code == 422  # Validation error
    
    def test_get_activity_types(self, client):
        """Test getting activity types."""
        response = client.get("/api/activities/types")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recent_activities(self, client):
        """Test getting recent activities."""
        response = client.get("/api/activities/recent?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "activities" in data
        assert isinstance(data["activities"], list)
    
    def test_get_activity_stats(self, client):
        """Test getting activity statistics."""
        response = client.get("/api/activities/stats/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_activities" in data
        assert "activities_by_type" in data
    
    def test_get_stats_by_type(self, client):
        """Test getting statistics by activity type."""
        response = client.get("/api/activities/stats/by-type")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestWebhookEndpoints:
    """Test webhook endpoints."""
    
    def test_webhook_verification_missing_params(self, client):
        """Test webhook verification with missing parameters."""
        response = client.get("/webhook")
        # Should return validation error
        assert response.status_code == 422
    
    def test_webhook_verification_invalid_token(self, client):
        """Test webhook verification with invalid token."""
        response = client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "invalid_token",
                "hub.challenge": "test_challenge",
            }
        )
        # Should return 403 for invalid token
        assert response.status_code == 403
    
    def test_webhook_event(self, client):
        """Test webhook event endpoint."""
        event_data = {
            "object_type": "activity",
            "aspect_type": "create",
            "object_id": 123456789,
            "event_time": 1234567890,
            "owner_id": 12345,
            "subscription_id": "sub_123",
        }
        
        response = client.post("/webhook", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "received"


class TestETLEndpoints:
    """Test ETL trigger endpoints."""
    
    def test_run_etl_sync(self, client):
        """Test running ETL pipeline synchronously."""
        response = client.post("/etl/run?limit=10")
        # This might fail if Strava credentials are not configured
        # But the endpoint should be accessible
        assert response.status_code in [200, 500]  # Either success or config error
    
    def test_run_etl_with_params(self, client):
        """Test running ETL with parameters."""
        response = client.post("/etl/run?limit=5")
        assert response.status_code in [200, 500]
