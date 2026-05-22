"""Unit tests for ETL pipeline."""
import pytest
from datetime import datetime
from app.etl.silver import SilverETL


@pytest.fixture
def sample_raw_activity():
    """Sample raw Strava activity data."""
    return {
        "id": 123456789,
        "name": "Morning Run",
        "type": "Run",
        "sport_type": "Running",
        "distance": 5000.0,
        "moving_time": 1800,
        "elapsed_time": 1900,
        "total_elevation_gain": 50.0,
        "average_speed": 2.78,
        "max_speed": 4.5,
        "average_heartrate": 145,
        "max_heartrate": 165,
        "start_date": "2024-01-15T08:00:00Z",
        "start_date_local": "2024-01-15T09:00:00",
        "timezone": "Europe/Berlin",
        "city": "Berlin",
        "country": "Germany",
        "trainer": False,
        "commute": False,
    }


@pytest.fixture
def silver_etl():
    """Create SilverETL instance."""
    return SilverETL()


class TestSilverETL:
    """Test SilverETL class."""
    
    def test_standardize_activity_type(self, silver_etl):
        """Test activity type standardization."""
        # Test standard types
        assert silver_etl.standardize_activity_type("Run") == "Running"
        assert silver_etl.standardize_activity_type("Ride") == "Cycling"
        assert silver_etl.standardize_activity_type("Swim") == "Swimming"
        assert silver_etl.standardize_activity_type("WeightTraining") == "Strength"
        
        # Test that unknown types are preserved
        assert silver_etl.standardize_activity_type("UnknownType") == "UnknownType"
    
    def test_validate_activity_data_valid(self, silver_etl, sample_raw_activity):
        """Test validation of valid activity data."""
        status, errors = silver_etl.validate_activity_data(sample_raw_activity)
        
        assert status == "valid"
        assert errors is None
    
    def test_validate_activity_data_missing_required(self, silver_etl):
        """Test validation with missing required fields."""
        invalid_data = {"id": 123}
        status, errors = silver_etl.validate_activity_data(invalid_data)
        
        assert status == "invalid"
        assert errors is not None
        assert len(errors) > 0
    
    def test_validate_activity_data_warnings(self, silver_etl, sample_raw_activity):
        """Test validation with warnings (missing optional fields)."""
        data_missing_optional = sample_raw_activity.copy()
        del data_missing_optional["distance"]
        
        status, errors = silver_etl.validate_activity_data(data_missing_optional)
        
        # Should be valid but with warnings (handled differently in implementation)
        assert status == "warning"
        assert errors is not None
    
    def test_clean_activity_data(self, silver_etl, sample_raw_activity):
        """Test data cleaning."""
        cleaned = silver_etl.clean_activity_data(sample_raw_activity)
        
        # Check that standardized type is added
        assert "standardized_type" in cleaned
        assert cleaned["standardized_type"] == "Running"
        
        # Check that metadata is added
        assert "cleaned_at" in cleaned
        
        # Check that original data is preserved
        assert cleaned["id"] == sample_raw_activity["id"]
        assert cleaned["name"] == sample_raw_activity["name"]
    
    def test_clean_activity_data_null_handling(self, silver_etl, sample_raw_activity):
        """Test that null values are handled properly."""
        data_with_nulls = sample_raw_activity.copy()
        data_with_nulls["distance"] = None
        data_with_nulls["average_speed"] = None
        
        cleaned = silver_etl.clean_activity_data(data_with_nulls)
        
        # Null numeric values should be replaced with 0
        assert cleaned["distance"] == 0.0
        assert cleaned["average_speed"] == 0.0
    
    def test_calculate_data_quality_score(self, silver_etl, sample_raw_activity):
        """Test data quality score calculation."""
        score = silver_etl.calculate_data_quality_score(sample_raw_activity)
        
        # Score should be between 0 and 1
        assert 0 <= score <= 1
        
        # Complete data should have high score
        assert score > 0.8
    
    def test_calculate_data_quality_score_low_quality(self, silver_etl):
        """Test data quality score for low quality data."""
        minimal_data = {
            "id": 123,
            "type": "Run",
            "name": "Test",
            "start_date": "2024-01-01T00:00:00Z",
        }
        
        score = silver_etl.calculate_data_quality_score(minimal_data)
        
        # Minimal data should have lower score
        assert score < 0.8
        assert score >= 0.0


class TestActivityTypeMapping:
    """Test activity type mapping."""
    
    def test_all_standard_types_mapped(self, silver_etl):
        """Test that all standard Strava types are mapped."""
        standard_types = [
            "Run", "Ride", "Swim", "WeightTraining", "Workout", "Walk",
            "Hike", "AlpineSki", "BackcountrySki", "VirtualRide", "VirtualRun",
        ]
        
        for activity_type in standard_types:
            mapped = silver_etl.standardize_activity_type(activity_type)
            assert mapped is not None
            assert isinstance(mapped, str)
