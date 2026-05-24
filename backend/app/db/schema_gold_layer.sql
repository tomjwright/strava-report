-- Gold Layer Schema - Dimensional Model for Strava Activity Analytics
-- This script creates the dimensional model tables

-- Drop existing tables if they exist (for clean slate)
DROP TABLE IF EXISTS fact_daily_summary CASCADE;
DROP TABLE IF EXISTS fact_activities CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_activity_type CASCADE;

-- Drop existing intermediate tables
DROP TABLE IF EXISTS silver_activities CASCADE;
DROP TABLE IF EXISTS bronze_activities CASCADE;
DROP TABLE IF EXISTS activities CASCADE;

-- Bronze Layer: Raw Strava data
CREATE TABLE bronze_activities (
    id SERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE,
    raw_data JSONB NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bronze_activities_activity_id ON bronze_activities(activity_id);
CREATE INDEX idx_bronze_activities_ingested_at ON bronze_activities(ingested_at);

-- Silver Layer: Cleaned and validated data
CREATE TABLE silver_activities (
    id SERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE,
    activity_name VARCHAR(255),
    type VARCHAR(100),
    sport_type VARCHAR(100),
    distance FLOAT,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain FLOAT,
    average_speed FLOAT,
    max_speed FLOAT,
    start_date TIMESTAMP WITH TIME ZONE,
    start_date_local TIMESTAMP WITH TIME ZONE,
    timezone VARCHAR(100),
    achievement_count INTEGER,
    kudos_count INTEGER,
    comment_count INTEGER,
    athlete_count INTEGER,
    photo_count INTEGER,
    trainer BOOLEAN DEFAULT FALSE,
    commute BOOLEAN DEFAULT FALSE,
    manual BOOLEAN DEFAULT FALSE,
    private BOOLEAN DEFAULT FALSE,
    flagged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_silver_activities_activity_id ON silver_activities(activity_id);
CREATE INDEX idx_silver_activities_type ON silver_activities(type);
CREATE INDEX idx_silver_activities_start_date ON silver_activities(start_date);

-- Dimension Table: dim_activity_type
CREATE TABLE dim_activity_type (
    activity_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    sport_type VARCHAR(100),
    category VARCHAR(50),
    is_distance_based BOOLEAN DEFAULT TRUE,
    unit_of_measure VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pre-populate with common activity types
INSERT INTO dim_activity_type (type_name, sport_type, category, is_distance_based, unit_of_measure, description) VALUES
('Run', 'Running', 'Endurance', TRUE, 'km', 'Running activities'),
('Ride', 'Cycling', 'Endurance', TRUE, 'km', 'Cycling activities'),
('Swim', 'Swimming', 'Endurance', TRUE, 'm', 'Swimming activities'),
('WeightTraining', 'WeightTraining', 'Strength', FALSE, 'minutes', 'Weight training sessions'),
('Walk', 'Walking', 'Endurance', TRUE, 'km', 'Walking activities'),
('Hike', 'Hiking', 'Endurance', TRUE, 'km', 'Hiking activities'),
('Yoga', 'Yoga', 'Flexibility', FALSE, 'minutes', 'Yoga sessions'),
('Workout', 'Workout', 'CrossTraining', FALSE, 'minutes', 'General workout sessions')
ON CONFLICT (type_name) DO NOTHING;

-- Dimension Table: dim_date
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date_actual DATE UNIQUE NOT NULL,
    day_of_week INTEGER,
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
    year_month INTEGER,
    year_quarter INTEGER,
    is_weekend BOOLEAN,
    hemisphere VARCHAR(10) DEFAULT 'Northern',
    season VARCHAR(15),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for dim_date
CREATE INDEX idx_dim_date_date_actual ON dim_date(date_actual);
CREATE INDEX idx_dim_date_year_month ON dim_date(year_month);
CREATE INDEX idx_dim_date_quarter ON dim_date(quarter);

-- Function to populate dim_date
CREATE OR REPLACE FUNCTION populate_dim_date(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    loop_date DATE := start_date;
BEGIN
    WHILE loop_date <= end_date LOOP
        INSERT INTO dim_date (
            date_id,
            date_actual,
            day_of_week,
            day_name,
            day_of_month,
            day_of_year,
            week_of_year,
            week_of_month,
            month,
            month_name,
            month_name_short,
            quarter,
            year,
            year_month,
            year_quarter,
            is_weekend,
            season
        ) VALUES (
            EXTRACT(YEAR FROM loop_date) * 10000 + 
            EXTRACT(MONTH FROM loop_date) * 100 + 
            EXTRACT(DAY FROM loop_date),
            loop_date,
            EXTRACT(DOW FROM loop_date),
            TO_CHAR(loop_date, 'Day'),
            EXTRACT(DAY FROM loop_date),
            EXTRACT(DOY FROM loop_date),
            EXTRACT(WEEK FROM loop_date),
            CEIL(EXTRACT(DAY FROM loop_date)::FLOAT / 7),
            EXTRACT(MONTH FROM loop_date),
            TO_CHAR(loop_date, 'Month'),
            TO_CHAR(loop_date, 'Mon'),
            EXTRACT(QUARTER FROM loop_date),
            EXTRACT(YEAR FROM loop_date),
            EXTRACT(YEAR FROM loop_date) * 100 + EXTRACT(MONTH FROM loop_date),
            EXTRACT(YEAR FROM loop_date) * 10 + EXTRACT(QUARTER FROM loop_date),
            EXTRACT(DOW FROM loop_date) IN (0, 6),
            CASE 
                WHEN EXTRACT(MONTH FROM loop_date) IN (12, 1, 2) THEN 'Winter'
                WHEN EXTRACT(MONTH FROM loop_date) IN (3, 4, 5) THEN 'Spring'
                WHEN EXTRACT(MONTH FROM loop_date) IN (6, 7, 8) THEN 'Summer'
                WHEN EXTRACT(MONTH FROM loop_date) IN (9, 10, 11) THEN 'Fall'
            END
        )
        ON CONFLICT (date_id) DO NOTHING;
        
        loop_date := loop_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Populate dim_date for 2026 (can be expanded as needed)
SELECT populate_dim_date('2026-01-01'::DATE, '2026-12-31'::DATE);

-- Fact Table: fact_activities
CREATE TABLE fact_activities (
    fact_id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    
    -- Foreign Keys to Dimensions
    activity_type_id INTEGER,
    date_id INTEGER,
    
    -- Raw Fields (for drill-down)
    activity_name VARCHAR(255),
    sport_type VARCHAR(100),
    timezone VARCHAR(100),
    
    -- Performance Metrics (Gold layer calculated fields)
    distance_m FLOAT,
    distance_km FLOAT,
    duration_seconds INTEGER,
    duration_minutes FLOAT,
    duration_hours FLOAT,
    elevation_gain_m FLOAT,
    average_speed_mps FLOAT,
    average_speed_kmh FLOAT,
    max_speed_mps FLOAT,
    max_speed_kmh FLOAT,
    average_pace_min_km FLOAT,
    average_pace_min_100m FLOAT,
    
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

-- Create indexes for fact_activities
CREATE INDEX idx_fact_activities_date_id ON fact_activities(date_id);
CREATE INDEX idx_fact_activities_activity_type_id ON fact_activities(activity_type_id);
CREATE INDEX idx_fact_activities_start_date ON fact_activities(start_date);
CREATE INDEX idx_fact_activities_sport_type ON fact_activities(sport_type);

-- Aggregated Fact Table: fact_daily_summary
CREATE TABLE fact_daily_summary (
    summary_id BIGSERIAL PRIMARY KEY,
    date_id INTEGER,
    
    -- Daily Aggregates
    total_activities INTEGER DEFAULT 0,
    total_distance_km FLOAT DEFAULT 0,
    total_duration_hours FLOAT DEFAULT 0,
    total_elevation_gain_m FLOAT DEFAULT 0,
    
    -- Averages
    average_distance_km FLOAT,
    average_duration_hours FLOAT,
    average_speed_kmh FLOAT,
    
    -- By Activity Type (JSONB for flexibility)
    activity_breakdown JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_daily_summary_date FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    CONSTRAINT uk_date_summary UNIQUE (date_id)
);

-- Create indexes for fact_daily_summary
CREATE INDEX idx_fact_daily_summary_date_id ON fact_daily_summary(date_id);
CREATE INDEX idx_fact_daily_summary_year_month ON fact_daily_summary(date_id);