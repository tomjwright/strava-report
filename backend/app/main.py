"""FastAPI application for Strava Report dashboard."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime

from app.config import settings
from app.db.database import db
from app.services.strava_client import strava_client
from app.etl.bronze import run_bronze_ingestion

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Strava activity dashboard (using Supabase client)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Strava activity dashboard (using Supabase client)",
        "database": "Supabase client",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "Supabase client",
        "tables_exist": db.table_exists('activities') if db else False,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/activities")
async def get_activities(limit: int = 100, activity_type: str = None):
    """Get activities from database."""
    try:
        activities = db.get_activities(limit=limit, activity_type=activity_type)
        return {"status": "success", "data": activities, "count": len(activities)}
    except Exception as e:
        logger.error(f"Error getting activities: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/bronze-activities")
async def get_bronze_activities(limit: int = 100):
    """Get raw activities from bronze layer."""
    try:
        if not db:
            return {"status": "error", "message": "Database not available"}
        
        response = db.client.table('bronze_activities').select('*').limit(limit).order('ingested_at', desc=True).execute()
        return {"status": "success", "data": response.data, "count": len(response.data)}
    except Exception as e:
        logger.error(f"Error getting bronze activities: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/ingest")
async def ingest_activity():
    """Test ingestion of a sample activity."""
    try:
        # Sample activity data
        sample_activity = {
            "id": 123456789,
            "name": "Test Activity",
            "type": "Run",
            "sport_type": "Running",
            "distance": 5000.0,
            "moving_time": 1800,
            "start_date": "2024-01-15T08:00:00Z",
            "start_date_local": "2024-01-15T09:00:00",
        }
        
        if db and db.table_exists('bronze_activities'):
            result = db.insert_activity(sample_activity)
            return {"status": "success", "message": "Activity ingested", "data": result}
        else:
            return {"status": "error", "message": "Tables not created yet. Create tables in Supabase SQL Editor."}
            
    except Exception as e:
        logger.error(f"Error ingesting activity: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/fetch-strava")
async def fetch_strava_data(limit: int = 10):
    """Fetch activities from Strava API (from 2026 onwards) and ingest them."""
    try:
        logger.info(f"Fetching up to {limit} activities from Strava (2026 onwards)")
        
        # Run bronze ingestion which will use Strava client
        result = run_bronze_ingestion(limit=limit)
        
        return {
            "status": "success",
            "message": f"Fetched and ingested {result['ingested']} activities from Strava",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error fetching Strava data: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=8003,  # Use port 8003 to avoid conflicts
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
