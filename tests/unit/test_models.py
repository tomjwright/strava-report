"""Unit tests for Pydantic models."""
import pytest
from datetime import datetime
from app.models.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityFilter,
    ActivityStats,
    ActivityTypeBreakdown,
)


class TestActivityCreate:
    """Test ActivityCreate model."""
    
    def test_valid_activity_create(self):
        """Test creating a valid Activity model."""
        activity = ActivityCreate(
            strava_id=123456789,
            activity_type="Running",
            sport_type="Run",
            name="Morning Run",
            start_date=datetime.utcnow(),
            start_date_local=datetime.utcnow(),
        )
        
        assert activity.strava_id == 123456789
        assert activity.activity_type == "Running"
        assert activity.name == "Morning Run"
    
    def test_activity_create_with_optional_fields(self):
        """Test ActivityCreate with optional fields."""
        activity = ActivityCreate(
            strava_id=123456789,
            activity_type="Running",
            sport_type="Run",
            name="Morning Run",
            description="Easy run in the park",
            distance=5000.0,
            moving_time=1800,
            start_date=datetime.utcnow(),
            start_date_local=datetime.utcnow(),
            timezone="Europe/Berlin",
        )
        
        assert activity.description == "Easy run in the park"
        assert activity.distance == 5000.0
        assert activity.moving_time == 1800


class TestActivityUpdate:
    """Test ActivityUpdate model."""
    
    def test_valid_activity_update(self):
        """Test creating a valid ActivityUpdate model."""
        update = ActivityUpdate(name="Updated Activity Name")
        assert update.name == "Updated Activity Name"
    
    def test_activity_update_all_fields(self):
        """Test ActivityUpdate with all fields."""
        update = ActivityUpdate(
            name="Updated Name",
            description="Updated Description",
            activity_type="Cycling",
        )
        
        assert update.name == "Updated Name"
        assert update.description == "Updated Description"
        assert update.activity_type == "Cycling"
    
    def test_activity_update_partial(self):
        """Test ActivityUpdate with partial fields."""
        update = ActivityUpdate()
        
        assert update.name is None
        assert update.description is None
        assert update.activity_type is None


class TestActivityFilter:
    """Test ActivityFilter model."""
    
    def test_valid_activity_filter(self):
        """Test creating a valid ActivityFilter model."""
        filter = ActivityFilter(
            activity_type="Running",
            limit=50,
            offset=0,
        )
        
        assert filter.activity_type == "Running"
        assert filter.limit == 50
        assert filter.offset == 0
    
    def test_activity_filter_defaults(self):
        """Test ActivityFilter default values."""
        filter = ActivityFilter()
        
        assert filter.activity_type is None
        assert filter.sport_type is None
        assert filter.limit == 100
        assert filter.offset == 0
    
    def test_activity_filter_date_range(self):
        """Test ActivityFilter with date range."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        filter = ActivityFilter(
            start_date=start_date,
            end_date=end_date,
        )
        
        assert filter.start_date == start_date
        assert filter.end_date == end_date
    
    def test_activity_filter_limit_validation(self):
        """Test ActivityFilter limit validation."""
        # Valid limits
        ActivityFilter(limit=1)
        ActivityFilter(limit=500)
        ActivityFilter(limit=1000)
        
        # Invalid limits
        with pytest.raises(ValueError):
            ActivityFilter(limit=0)
        
        with pytest.raises(ValueError):
            ActivityFilter(limit=1001)
    
    def test_activity_filter_offset_validation(self):
        """Test ActivityFilter offset validation."""
        # Valid offsets
        ActivityFilter(offset=0)
        ActivityFilter(offset=100)
        
        # Invalid offset
        with pytest.raises(ValueError):
            ActivityFilter(offset=-1)
    
    def test_activity_filter_activity_type_validation(self):
        """Test ActivityFilter activity type validation."""
        # Valid activity types
        ActivityFilter(activity_type="Run")
        ActivityFilter(activity_type="Ride")
        ActivityFilter(activity_type="Swim")
        ActivityFilter(activity_type="WeightTraining")
        
        # Invalid activity type
        with pytest.raises(ValueError):
            ActivityFilter(activity_type="InvalidType")


class TestActivityStats:
    """Test ActivityStats model."""
    
    def test_valid_activity_stats(self):
        """Test creating a valid ActivityStats model."""
        stats = ActivityStats(
            total_activities=100,
            total_distance=50000.0,
            total_moving_time=36000,
            total_elevation_gain=1000.0,
        )
        
        assert stats.total_activities == 100
        assert stats.total_distance == 50000.0
        assert stats.total_moving_time == 36000
        assert stats.activities_by_type == {}
    
    def test_activity_stats_with_breakdown(self):
        """Test ActivityStats with activity type breakdown."""
        stats = ActivityStats(
            total_activities=100,
            total_distance=50000.0,
            activities_by_type={"Running": 50, "Cycling": 30, "Swimming": 20},
        )
        
        assert stats.activities_by_type["Running"] == 50
        assert stats.activities_by_type["Cycling"] == 30
        assert stats.activities_by_type["Swimming"] == 20


class TestActivityTypeBreakdown:
    """Test ActivityTypeBreakdown model."""
    
    def test_valid_activity_type_breakdown(self):
        """Test creating a valid ActivityTypeBreakdown model."""
        breakdown = ActivityTypeBreakdown(
            activity_type="Running",
            count=50,
            total_distance=25000.0,
            total_moving_time=18000,
        )
        
        assert breakdown.activity_type == "Running"
        assert breakdown.count == 50
        assert breakdown.total_distance == 25000.0
