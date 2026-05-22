# Dimensional Model for Strava Activity Analytics

## Overview
This document defines the dimensional model for the Gold layer of the Strava activity data warehouse.

## Schema Design

### Fact Table: `fact_activities`

**Purpose**: Central fact table containing all activity metrics with foreign keys to dimensions

**Schema**:
```sql
CREATE TABLE fact_activities (
    fact_id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL, -- Strava activity ID (natural key)
    
    -- Foreign Keys to Dimensions
    activity_type_id INTEGER REFERENCES dim_activity_type(activity_type_id),
    date_id INTEGER REFERENCES dim_date(date_id),
    
    -- Raw Fields (for drill-down)
    activity_name VARCHAR(255),
    sport_type VARCHAR(100),
    timezone VARCHAR(100),
    
    -- Performance Metrics (Gold layer calculated fields)
    distance_m FLOAT, -- distance in meters
    distance_km FLOAT, -- distance in kilometers (calculated)
    duration_seconds INTEGER, -- moving time in seconds
    duration_minutes FLOAT, -- moving time in minutes (calculated)
    duration_hours FLOAT, -- moving time in hours (calculated)
    elevation_gain_m FLOAT, -- total elevation gain in meters
    average_speed_mps FLOAT, -- average speed in meters per second
    average_speed_kmh FLOAT, -- average speed in km/h (calculated)
    max_speed_mps FLOAT, -- max speed in meters per second
    max_speed_kmh FLOAT, -- max speed in km/h (calculated)
    average_pace_min_km FLOAT, -- average pace (min/km) for running
    average_pace_min_100m FLOAT, -- average pace (min/100m) for swimming
    
    -- Social Metrics
    kudos_count INTEGER,
    comment_count INTEGER,
    achievement_count INTEGER,
    photo_count INTEGER,
    athlete_count INTEGER,
    
    -- Boolean Flags
    is_trainer BOOLEAN DEFAULT FALSE,
    is_commute BOOLEAN DEFAULT FALSE,
    is_manual BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    start_date TIMESTAMP WITH TIME ZONE,
    start_date_local TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_activities_type FOREIGN KEY (activity_type_id) REFERENCES dim_activity_type(activity_type_id),
    CONSTRAINT fk_activities_date FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    CONSTRAINT uk_activity_id UNIQUE (activity_id)
);

-- Indexes
CREATE INDEX idx_fact_activities_date_id ON fact_activities(date_id);
CREATE INDEX idx_fact_activities_activity_type_id ON fact_activities(activity_type_id);
CREATE INDEX idx_fact_activities_start_date ON fact_activities(start_date);
CREATE INDEX idx_fact_activities_sport_type ON fact_activities(sport_type);
```

### Dimension Table: `dim_activity_type`

**Purpose**: Dimension for activity types (Run, Swim, Ride, etc.)

**Schema**:
```sql
CREATE TABLE dim_activity_type (
    activity_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    sport_type VARCHAR(100),
    category VARCHAR(50), -- Endurance, Strength, Flexibility, etc.
    is_distance_based BOOLEAN DEFAULT TRUE,
    unit_of_measure VARCHAR(20), -- km, meters, reps, etc.
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pre-populate with common activity types
INSERT INTO dim_activity_type (type_name, sport_type, category, is_distance_based, unit_of_measure, description) VALUES
('Run', 'Running', 'Endurance', TRUE, 'km', 'Running activities'),
('Ride', 'Cycling', 'Endurance', TRUE, 'km', 'Cycling activities'),
('Swim', 'Swimming', 'Endurance', TRUE, 'm', 'Swimming activities'),
('WeightTraining', 'WeightTraining', 'Strength', FALSE, 'reps', 'Weight training sessions'),
('Walk', 'Walking', 'Endurance', TRUE, 'km', 'Walking activities'),
('Hike', 'Hiking', 'Endurance', TRUE, 'km', 'Hiking activities'),
('Yoga', 'Yoga', 'Flexibility', FALSE, 'minutes', 'Yoga sessions'),
('Workout', 'Workout', 'CrossTraining', FALSE, 'minutes', 'General workout sessions');
```

### Dimension Table: `dim_date`

**Purpose**: Date dimension for time-based analysis (daily rollups, trends, etc.)

**Schema**:
```sql
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY, -- YYYYMMDD format (e.g., 20260115)
    date_actual DATE UNIQUE NOT NULL,
    
    -- Date Attributes
    day_of_week INTEGER, -- 1-7 (Monday-Sunday)
    day_name VARCHAR(10),
    day_of_month INTEGER,
    day_of_year INTEGER,
    
    week_of_year INTEGER,
    week_of_month INTEGER,
    
    month INTEGER,
    month_name VARCHAR(15),
    month_name_short VARCHAR(3),
    quarter INTEGER,
    
    year INTEGER,
    year_month INTEGER, -- YYYYMM format
    year_quarter INTEGER, -- YYYYQ format
    
    -- Weekend Indicator
    is_weekend BOOLEAN,
    
    -- Season
    hemisphere VARCHAR(10), -- Northern, Southern
    season VARCHAR(15), -- Spring, Summer, Fall, Winter
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_dim_date_date_actual ON dim_date(date_actual);
CREATE INDEX idx_dim_date_year_month ON dim_date(year_month);
CREATE INDEX idx_dim_date_quarter ON dim_date(quarter);
```

### Aggregated Fact Tables: `fact_daily_summary`

**Purpose**: Daily aggregations for quick dashboard metrics

**Schema**:
```sql
CREATE TABLE fact_daily_summary (
    summary_id BIGSERIAL PRIMARY KEY,
    date_id INTEGER REFERENCES dim_date(date_id),
    
    -- Daily Aggregates
    total_activities INTEGER DEFAULT 0,
    total_distance_km FLOAT DEFAULT 0,
    total_duration_hours FLOAT DEFAULT 0,
    total_elevation_gain_m FLOAT DEFAULT 0,
    
    -- Averages
    average_distance_km FLOAT,
    average_duration_hours FLOAT,
    average_speed_kmh FLOAT,
    
    -- By Activity Type (could be separate table or JSON)
    activity_breakdown JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_daily_summary_date FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    CONSTRAINT uk_date_summary UNIQUE (date_id)
);

-- Indexes
CREATE INDEX idx_fact_daily_summary_date_id ON fact_daily_summary(date_id);
CREATE INDEX idx_fact_daily_summary_year_month ON fact_daily_summary(
    (SELECT year_month FROM dim_date WHERE dim_date.date_id = fact_daily_summary.date_id)
);
```

## ETL Pipeline

### Bronze Layer
- **Source**: Strava API
- **Format**: Raw JSON exactly as received from Strava
- **Table**: `bronze_activities`
- **Update Frequency**: Daily (incremental)

### Silver Layer  
- **Source**: Bronze layer
- **Transformations**: 
  - Data validation and cleaning
  - Type conversion
  - Standardization of field names
  - Removing sensitive fields
- **Table**: `silver_activities`
- **Update Frequency**: Daily (incremental)

### Gold Layer
- **Source**: Silver layer
- **Transformations**:
  - Business logic calculations (pace, speed conversions)
  - Dimension lookup (activity_type_id, date_id)
  - Metric aggregations
  - Data quality checks
- **Tables**: 
  - `dim_activity_type` (dimension)
  - `dim_date` (dimension) 
  - `fact_activities` (fact table)
  - `fact_daily_summary` (aggregated facts)
- **Update Frequency**: Daily (incremental + full refresh for dimensions)

## Dashboard Data Access

The frontend dashboard should query the Gold layer:

1. **Activity Details**: Query `fact_activities` with joins to dimensions
2. **Daily Metrics**: Query `fact_daily_summary` for quick aggregations
3. **Trends Analysis**: Query `fact_activities` grouped by `dim_date` attributes
4. **Activity Breakdown**: Query `fact_activities` grouped by `dim_activity_type`

## Benefits of This Model

1. **Performance**: Pre-calculated metrics and aggregations
2. **Flexibility**: Dimensional model enables various analyses
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Can add more dimensions/facts as needed
5. **Data Quality**: Validation at each layer
6. **Business Logic**: Centralized in Gold layer transformations
