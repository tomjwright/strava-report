"""
Fix database schema using Supabase REST API
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_SERVICE_KEY:
    print("ERROR: SUPABASE_SERVICE_KEY not found in .env")
    exit(1)

# Construct the SQL endpoint
sql_endpoint = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"

# SQL statements to fix the schema
sql_statements = [
    "ALTER TABLE bronze_activities ALTER COLUMN activity_id TYPE BIGINT USING activity_id::BIGINT;",
    "ALTER TABLE activities ALTER COLUMN activity_id TYPE BIGINT USING activity_id::BIGINT;"
]

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

print("Attempting to fix database schema...")
print(f"Supabase URL: {SUPABASE_URL}")

# Try using the /rest/v1/sql endpoint instead
sql_endpoint_direct = f"{SUPABASE_URL}/rest/v1/sql"

for i, sql in enumerate(sql_statements):
    print(f"\nExecuting SQL statement {i+1}:")
    print(f"SQL: {sql}")
    
    try:
        response = requests.post(
            sql_endpoint_direct,
            headers=headers,
            json={"query": sql},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print(f"[SUCCESS] SQL statement {i+1} executed successfully")
        else:
            print(f"[ERROR] Failed to execute SQL statement {i+1}")
            
    except Exception as e:
        print(f"Exception: {e}")
        print("Failed to execute SQL via REST API")

print("\nIf the above failed, please execute these SQL statements manually in Supabase SQL Editor:")
for sql in sql_statements:
    print(f"  {sql}")
