"""Simple backend - direct SQL queries like Power BI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI(title="Simple Strava Dashboard API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

@app.get("/api/activities")
def get_activities(limit: int = 100):
    """Get activities like Power BI query."""
    try:
        response = supabase.table('strava_activities')\
            .select('*')\
            .order('start_date', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "status": "success", 
            "data": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/summary")
def get_summary():
    """Get summary statistics."""
    try:
        # Get all activities
        response = supabase.table('strava_activities').select('*').execute()
        activities = response.data
        
        if not activities:
            return {"status": "success", "data": {}}
        
        # Calculate summary
        total_activities = len(activities)
        total_distance = sum(a.get('distance_km', 0) for a in activities)
        total_time = sum(a.get('moving_time_minutes', 0) for a in activities)
        total_elevation = sum(a.get('total_elevation_gain_m', 0) for a in activities)
        
        # Activity type breakdown
        activity_types = {}
        for activity in activities:
            atype = activity.get('type', 'Unknown')
            if atype not in activity_types:
                activity_types[atype] = 0
            activity_types[atype] += 1
        
        return {
            "status": "success",
            "data": {
                "total_activities": total_activities,
                "total_distance_km": round(total_distance, 2),
                "total_time_hours": round(total_time / 60, 2),
                "total_elevation_m": round(total_elevation, 2),
                "activity_types": activity_types,
                "recent_date": activities[0].get('start_date_local') if activities else None
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/reload-data")
def reload_data():
    """Trigger data reload (run the simple loader)."""
    return {"status": "success", "message": "Run simple_data_loader.py manually"}

@app.get("/health")
def health():
    """Health check."""
    try:
        # Test database connection
        response = supabase.table('strava_activities').select('id').limit(1).execute()
        tables_exist = len(response.data) >= 0  # Just check if query works
        
        return {
            "status": "healthy",
            "database": "Supabase connected",
            "tables_exist": tables_exist,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)