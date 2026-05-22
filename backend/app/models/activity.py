"""Pydantic models for Activity API requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ActivityBase(BaseModel):
    """Base activity model with common fields."""
    strava_id: int = Field(..., description="Strava activity ID")
    activity_type: str = Field(..., description="Activity type")
    sport_type: str = Field(..., description="Sport type")
    name: str = Field(..., description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    distance: Optional[float] = Field(None, description="Distance in meters")
    moving_time: Optional[int] = Field(None, description="Moving time in seconds")
    elapsed_time: Optional[int] = Field(None, description="Elapsed time in seconds")
    total_elevation_gain: Optional[float] = Field(None, description="Total elevation gain in meters")


class ActivityCreate(ActivityBase):
    """Model for creating a new activity."""
    start_date: datetime = Field(..., description="Activity start date in UTC")
    start_date_local: datetime = Field(..., description="Activity start date local time")
    timezone: Optional[str] = Field(None, description="Timezone")


class ActivityUpdate(BaseModel):
    """Model for updating an existing activity."""
    name: Optional[str] = Field(None, description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    activity_type: Optional[str] = Field(None, description="Activity type")


class ActivityResponse(ActivityBase):
    """Model for activity response."""
    id: str = Field(..., description="Database ID")
    start_date: datetime = Field(..., description="Activity start date in UTC")
    start_date_local: datetime = Field(..., description="Activity start date local time")
    timezone: Optional[str] = Field(None, description="Timezone")
    
    # Performance metrics
    average_speed: Optional[float] = Field(None, description="Average speed in m/s")
    max_speed: Optional[float] = Field(None, description="Maximum speed in m/s")
    average_heartrate: Optional[float] = Field(None, description="Average heart rate in bpm")
    max_heartrate: Optional[int] = Field(None, description="Maximum heart rate in bpm")
    average_cadence: Optional[float] = Field(None, description="Average cadence")
    average_watts: Optional[float] = Field(None, description="Average power in watts")
    max_watts: Optional[int] = Field(None, description="Maximum power in watts")
    weighted_average_watts: Optional[float] = Field(None, description="Weighted average power in watts")
    kilojoules: Optional[float] = Field(None, description="Energy expenditure in kilojoules")
    
    # Location
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country")
    
    # Social metrics
    kudos_count: Optional[int] = Field(None, description="Number of kudos")
    comment_count: Optional[int] = Field(None, description="Number of comments")
    achievement_count: Optional[int] = Field(None, description="Number of achievements")
    
    # Timestamps
    created_at: datetime = Field(..., description="Record creation time")
    updated_at: datetime = Field(..., description="Record update time")
    
    class Config:
        from_attributes = True


class ActivityFilter(BaseModel):
    """Model for filtering activities."""
    activity_type: Optional[str] = Field(None, description="Filter by activity type")
    sport_type: Optional[str] = Field(None, description="Filter by sport type")
    start_date: Optional[datetime] = Field(None, description="Filter activities after this date")
    end_date: Optional[datetime] = Field(None, description="Filter activities before this date")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    
    @field_validator('activity_type')
    @classmethod
    def validate_activity_type(cls, v):
        """Validate activity type."""
        if v is not None:
            valid_types = ['Run', 'Ride', 'Swim', 'WeightTraining', 'Workout', 'Walk', 'Hike', 'AlpineSki', 'BackcountrySki', 'Canoeing', 'Crossfit', 'EBikeRide', 'Elliptical', 'Golf', 'Handcycle', 'HangGliding', 'IceSkate', 'InlineSkate', 'Kayaking', 'Kitesurf', 'NordicSki', 'RockClimbing', 'RollerSki', 'Rowing', 'Sail', 'Skateboard', 'Snowboard', 'Snowshoe', 'Soccer', 'StandUpPaddling', 'StairStepper', 'Surfing', 'Swim', 'TableTennis', 'Tennis', 'TrailRun', 'VirtualRide', 'VirtualRun', 'Walk', 'WaterSki', 'Wheelchair', 'Windsurf', 'Workout', 'Yoga']
            if v not in valid_types:
                raise ValueError(f"Invalid activity type. Must be one of: {', '.join(valid_types)}")
        return v


class ActivityListResponse(BaseModel):
    """Model for paginated activity list response."""
    activities: List[ActivityResponse]
    total: int = Field(..., description="Total number of activities matching the filter")
    limit: int = Field(..., description="Maximum number of results returned")
    offset: int = Field(..., description="Offset used for pagination")


class ActivityStats(BaseModel):
    """Model for activity statistics."""
    total_activities: int = Field(..., description="Total number of activities")
    total_distance: Optional[float] = Field(None, description="Total distance in meters")
    total_moving_time: Optional[int] = Field(None, description="Total moving time in seconds")
    total_elevation_gain: Optional[float] = Field(None, description="Total elevation gain in meters")
    
    # Averages
    average_distance: Optional[float] = Field(None, description="Average distance in meters")
    average_moving_time: Optional[int] = Field(None, description="Average moving time in seconds")
    average_speed: Optional[float] = Field(None, description="Average speed in m/s")
    
    # Counts by type
    activities_by_type: dict = Field(default_factory=dict, description="Count of activities by type")


class ActivityTypeBreakdown(BaseModel):
    """Model for activity breakdown by type."""
    activity_type: str = Field(..., description="Activity type")
    count: int = Field(..., description="Number of activities")
    total_distance: Optional[float] = Field(None, description="Total distance in meters")
    total_moving_time: Optional[int] = Field(None, description="Total moving time in seconds")
    average_distance: Optional[float] = Field(None, description="Average distance in meters")
    average_speed: Optional[float] = Field(None, description="Average speed in m/s")
