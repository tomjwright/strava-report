"""Bronze layer ETL: Raw data ingestion from Strava API using Supabase client."""
from typing import List, Dict, Any, Optional
from loguru import logger

from app.db.supabase_adapter import db
from app.services.strava_client import strava_client


def ingest_activity(activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Ingest a single activity into bronze layer.
    
    Args:
        activity_data: Raw activity data from Strava API
        
    Returns:
        Inserted record or None if failed
    """
    try:
        if not db:
            logger.error("Database not available")
            return None
        
        # Insert using Supabase client
        result = db.insert_activity(activity_data)
        logger.info(f"Ingested activity {activity_data['id']} into bronze layer")
        return result
        
    except Exception as e:
        logger.error(f"Failed to ingest activity {activity_data.get('id', 'unknown')}: {e}")
        return None


def ingest_activities(activities_data: List[Dict[str, Any]]) -> int:
    """Ingest multiple activities into bronze layer.
    
    Args:
        activities_data: List of raw activity data from Strava API
        
    Returns:
        Number of successfully ingested activities
    """
    success_count = 0
    for activity_data in activities_data:
        if ingest_activity(activity_data):
            success_count += 1
    
    logger.info(f"Ingested {success_count}/{len(activities_data)} activities into bronze layer")
    return success_count


def fetch_and_ingest_recent(
    limit: int = 100,
    after: Optional[int] = None,
) -> int:
    """Fetch recent activities from Strava and ingest into bronze layer.
    
    Args:
        limit: Maximum number of activities to fetch
        after: Unix timestamp to fetch activities after this date
        
    Returns:
        Number of successfully ingested activities
    """
    try:
        logger.info(f"Fetching {limit} recent activities from Strava")
        activities_data = strava_client.get_all_activities(
            max_activities=limit,
            after=after,
        )
        
        if not activities_data:
            logger.info("No activities found")
            return 0
        
        return ingest_activities(activities_data)
        
    except Exception as e:
        logger.error(f"Failed to fetch and ingest recent activities: {e}")
        raise


def run_bronze_ingestion(limit: int = 100, after: Optional[int] = None) -> Dict[str, Any]:
    """Run bronze layer ingestion.
    
    Args:
        limit: Maximum number of activities to fetch
        after: Unix timestamp to fetch activities after this date
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        ingested_count = fetch_and_ingest_recent(limit=limit, after=after)
        return {
            'ingested': ingested_count,
            'status': 'success',
            'error': None
        }
    except Exception as e:
        return {
            'ingested': 0,
            'status': 'error',
            'error': str(e)
        }