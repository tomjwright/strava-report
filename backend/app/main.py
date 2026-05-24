"""FastAPI application for Strava Report dashboard."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime

from app.config import settings
from app.db.database import db
from app.services.strava_client import strava_client
from app.etl.bronze import run_bronze_ingestion
from app.etl.silver import run_silver_transformation
from app.etl.gold import run_gold_transformation
from app.etl.orchestrator import run_full_etl_pipeline, run_health_check

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


@app.delete("/api/clear-data")
async def clear_database():
    """Clear all mock data from database to start fresh with real Strava data."""
    try:
        logger.info("Clearing all data from database")
        
        if not db:
            return {"status": "error", "message": "Database not available"}
        
        # Clear bronze_activities table
        try:
            result = db.client.table('bronze_activities').delete().execute()
            logger.info(f"Deleted {result.count if hasattr(result, 'count') else 'all'} records from bronze_activities")
        except Exception as e:
            logger.error(f"Error clearing bronze_activities: {e}")
        
        # Clear activities table  
        try:
            result = db.client.table('activities').delete().execute()
            logger.info(f"Deleted {result.count if hasattr(result, 'count') else 'all'} records from activities")
        except Exception as e:
            logger.error(f"Error clearing activities: {e}")
        
        return {
            "status": "success",
            "message": "Database cleared successfully. Ready to fetch real Strava data."
        }
        
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/transform-silver")
async def transform_silver_data(limit: int = 1000):
    """Transform bronze data to structured activities in the activities table."""
    try:
        logger.info(f"Starting silver layer transformation for up to {limit} activities")
        
        result = run_silver_transformation(limit=limit)
        
        return {
            "status": "success",
            "message": f"Transformed {result['transformed']} activities from bronze to silver layer",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error transforming silver data: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/run-etl-pipeline")
async def run_etl_pipeline(
    bronze_limit: int = 100,
    silver_limit: int = 100,
    gold_limit: int = 100,
    incremental: bool = True
):
    """Run the complete ETL pipeline: Bronze → Silver → Gold."""
    try:
        logger.info("Starting complete ETL pipeline")
        
        result = run_full_etl_pipeline(
            bronze_limit=bronze_limit,
            silver_limit=silver_limit,
            gold_limit=gold_limit,
            incremental=incremental
        )
        
        return {
            "status": result['overall_status'],
            "message": f"ETL pipeline completed with status: {result['overall_status']}",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error running ETL pipeline: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/etl-health")
async def etl_health_check():
    """Run health check on ETL pipeline components."""
    try:
        health_status = run_health_check()
        return {
            "status": health_status['overall_status'],
            "health_check": health_status
        }
        
    except Exception as e:
        logger.error(f"Error running health check: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/gold-activities")
async def get_gold_activities(limit: int = 100):
    """Get structured activities from the gold layer (dimensional model)."""
    try:
        if not db:
            return {"status": "error", "message": "Database not available"}
        
        # Get activities from gold fact table with dimension joins
        query = """
        SELECT 
            f.*,
            at.type_name as activity_type_name,
            at.category as activity_category,
            d.date_actual,
            d.day_name,
            d.month_name,
            d.year
        FROM fact_activities f
        LEFT JOIN dim_activity_type at ON f.activity_type_id = at.activity_type_id
        LEFT JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY f.start_date DESC
        LIMIT $1
        """

        # Since we can't run raw SQL through Supabase client, we'll do it manually
        # Get gold activities
        gold_result = db.client.table('fact_activities').select('*').order('start_date', desc=True).limit(limit).execute()

        return {"status": "success", "data": gold_result.data, "count": len(gold_result.data)}
    except Exception as e:
        logger.error(f"Error getting gold activities: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/daily-summary")
async def get_daily_summary(days: int = 30):
    """Get daily summary data from gold layer."""
    try:
        if not db:
            return {"status": "error", "message": "Database not available"}
        
        # Get daily summaries
        summary_result = db.client.table('fact_daily_summary').select('*').order('date_id', desc=True).limit(days).execute()
        
        return {"status": "success", "data": summary_result.data, "count": len(summary_result.data)}
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}")
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
