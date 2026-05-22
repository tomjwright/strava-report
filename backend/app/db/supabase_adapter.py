"""Simple database adapter using Supabase client (bypasses DNS issues)."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

class SupabaseDatabase:
    """Simple database adapter using Supabase client."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
    
    def insert_activity(self, activity_data):
        """Insert activity into bronze_activities table."""
        try:
            response = self.client.table('bronze_activities').insert({
                'activity_id': activity_data['id'],
                'raw_data': activity_data,
            }).execute()
            return response
        except Exception as e:
            print(f"Error inserting activity: {e}")
            return None
    
    def get_activities(self, limit=100, activity_type=None):
        """Get activities from the database."""
        try:
            query = self.client.table('activities').select('*')
            
            if activity_type:
                query = query.eq('activity_type', activity_type)
            
            query = query.limit(limit)
            query = query.order('start_date', desc=True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error getting activities: {e}")
            return []
    
    def table_exists(self, table_name):
        """Check if table exists."""
        try:
            response = self.client.table(table_name).select('*').limit(1).execute()
            return True
        except Exception as e:
            print(f"Table {table_name} check failed: {e}")
            return False


# Global instance
try:
    db = SupabaseDatabase()
    print("Supabase database adapter initialized successfully")
except Exception as e:
    print(f"Failed to initialize database: {e}")
    db = None