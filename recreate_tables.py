"""
Recreate database tables with correct BIGINT schema for activity IDs
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

# Get the connection string from the environment
# Since we're using Supabase, we need to construct the connection string
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Extract the database connection details from the Supabase URL
# Format: https://<project_id>.supabase.co
db_host = SUPABASE_URL.replace("https://", "").replace(".supabase.co", ".supabase.co")
db_port = "5432"
db_name = "postgres"
db_user = "postgres"
db_password = SUPABASE_SERVICE_KEY

print(f"Connecting to PostgreSQL database...")
print(f"Host: {db_host}")
print(f"Database: {db_name}")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Successfully connected to database")
    
    # Drop existing tables if they exist
    drop_statements = [
        "DROP TABLE IF EXISTS bronze_activities CASCADE;",
        "DROP TABLE IF EXISTS activities CASCADE;"
    ]
    
    for stmt in drop_statements:
        print(f"Executing: {stmt}")
        cursor.execute(stmt)
    
    # Create bronze_activities table with correct schema
    create_bronze = """
    CREATE TABLE bronze_activities (
        id SERIAL PRIMARY KEY,
        activity_id BIGINT NOT NULL UNIQUE,
        raw_data JSONB NOT NULL,
        ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    print(f"Creating bronze_activities table...")
    cursor.execute(create_bronze)
    
    # Create activities table with correct schema
    create_activities = """
    CREATE TABLE activities (
        id SERIAL PRIMARY KEY,
        activity_id BIGINT NOT NULL UNIQUE,
        name TEXT,
        type TEXT,
        sport_type TEXT,
        distance FLOAT,
        moving_time INTEGER,
        elapsed_time INTEGER,
        total_elevation_gain FLOAT,
        average_speed FLOAT,
        max_speed FLOAT,
        start_date TIMESTAMP WITH TIME ZONE,
        start_date_local TIMESTAMP WITH TIME ZONE,
        timezone TEXT,
        achievement_count INTEGER,
        kudos_count INTEGER,
        comment_count INTEGER,
        athlete_count INTEGER,
        photo_count INTEGER,
        trainer BOOLEAN,
        commute BOOLEAN,
        manual BOOLEAN,
        private BOOLEAN,
        flagged BOOLEAN,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    print(f"Creating activities table...")
    cursor.execute(create_activities)
    
    # Create indexes
    index_statements = [
        "CREATE INDEX idx_bronze_activities_activity_id ON bronze_activities(activity_id);",
        "CREATE INDEX idx_bronze_activities_ingested_at ON bronze_activities(ingested_at);",
        "CREATE INDEX idx_activities_activity_id ON activities(activity_id);",
        "CREATE INDEX idx_activities_start_date ON activities(start_date);",
        "CREATE INDEX idx_activities_type ON activities(type);"
    ]
    
    for stmt in index_statements:
        print(f"Creating index: {stmt}")
        cursor.execute(stmt)
    
    print("\n[SUCCESS] Database schema fixed successfully!")
    print("Tables created with BIGINT activity_id columns")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nIf direct PostgreSQL connection fails, please execute this SQL manually in Supabase SQL Editor:")
    
    manual_sql = """
-- Drop existing tables
DROP TABLE IF EXISTS bronze_activities CASCADE;
DROP TABLE IF EXISTS activities CASCADE;

-- Create bronze_activities table with correct schema
CREATE TABLE bronze_activities (
    id SERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE,
    raw_data JSONB NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create activities table with correct schema
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE,
    name TEXT,
    type TEXT,
    sport_type TEXT,
    distance FLOAT,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain FLOAT,
    average_speed FLOAT,
    max_speed FLOAT,
    start_date TIMESTAMP WITH TIME ZONE,
    start_date_local TIMESTAMP WITH TIME ZONE,
    timezone TEXT,
    achievement_count INTEGER,
    kudos_count INTEGER,
    comment_count INTEGER,
    athlete_count INTEGER,
    photo_count INTEGER,
    trainer BOOLEAN,
    commute BOOLEAN,
    manual BOOLEAN,
    private BOOLEAN,
    flagged BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_bronze_activities_activity_id ON bronze_activities(activity_id);
CREATE INDEX idx_bronze_activities_ingested_at ON bronze_activities(ingested_at);
CREATE INDEX idx_activities_activity_id ON activities(activity_id);
CREATE INDEX idx_activities_start_date ON activities(start_date);
CREATE INDEX idx_activities_type ON activities(type);
    """
    
    print(manual_sql)
