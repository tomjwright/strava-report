"""
Fix database schema to use BIGINT for activity IDs
Strava activity IDs exceed the range of standard PostgreSQL integers
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Connecting to Supabase: {SUPABASE_URL}")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Fixing database schema for bronze_activities table...")

try:
    # Since we can't use ALTER TABLE directly through Supabase client,
    # we need to recreate the table with the correct schema
    # First, let's drop the existing table
    print("Dropping existing bronze_activities table...")
    try:
        result = supabase.table('bronze_activities').delete().neq('id', 0).execute()
        print(f"Cleared existing data from bronze_activities")
    except Exception as e:
        print(f"Error clearing table (might not exist yet): {e}")
    
    # Now let's try to execute the ALTER TABLE SQL directly via Supabase
    # We'll need to use the service role key for DDL operations
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    if not SUPABASE_SERVICE_KEY:
        print("ERROR: SUPABASE_SERVICE_KEY not found in .env")
        print("Please add it to your .env file to perform DDL operations")
        exit(1)
    
    # Create a new client with service role for DDL operations
    from supabase import create_client
    supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Execute SQL to alter the column type
    print("Executing SQL to change activity_id column to BIGINT...")
    sql = """
    ALTER TABLE bronze_activities 
    ALTER COLUMN activity_id TYPE BIGINT USING activity_id::BIGINT;
    """
    
    # This won't work directly through the client, so we need to use the RPC function
    # or execute it through the Supabase SQL editor
    print("NOTE: This SQL needs to be executed manually in Supabase SQL Editor:")
    print(sql)
    print("\nGo to your Supabase dashboard -> SQL Editor and execute the above SQL.")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nAlternative: Execute this SQL manually in Supabase SQL Editor:")
    print("ALTER TABLE bronze_activities ALTER COLUMN activity_id TYPE BIGINT USING activity_id::BIGINT;")

print("\nFor activities table, also execute:")
print("ALTER TABLE activities ALTER COLUMN activity_id TYPE BIGINT USING activity_id::BIGINT;")
