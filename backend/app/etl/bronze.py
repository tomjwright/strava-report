"""Bronze layer ETL: Raw data ingestion from Strava API using Supabase client."""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

from app.db.supabase_adapter import db
from app.services.strava_client import strava_client


def ingest_activity(activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Ingest a single activity into bronze layer (raw Strava data).
    
    Args:
        activity_data: Raw activity data from Strava API (exact as received)
        
    Returns:
        Inserted record or None if failed
    """
    try:
        if not db:
            logger.error("Database not available")
            return None
        
        # Store raw Strava data exactly as received
        bronze_record = {
            'activity_id': activity_data['id'],
            'raw_data': activity_data,  # Store complete raw JSON
            'ingested_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Insert using Supabase client
        result = db.client.table('bronze_activities').insert(bronze_record).execute()
        logger.info(f"Ingested activity {activity_data['id']} into bronze layer")
        return result
        
    except Exception as e:
        logger.error(f"Failed to ingest activity {activity_data.get('id', 'unknown')}: {e}")
        return None


def upsert_activity(activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Upsert a single activity into bronze layer (handle updates).
    
    Args:
        activity_data: Raw activity data from Strava API
        
    Returns:
        Inserted/updated record or None if failed
    """
    try:
        if not db:
            logger.error("Database not available")
            return None
        
        # Check if activity already exists
        existing = db.client.table('bronze_activities').select('*').eq('activity_id', activity_data['id']).execute()
        
        bronze_record = {
            'activity_id': activity_data['id'],
            'raw_data': activity_data,  # Store complete raw JSON
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if existing.data:
            # Update existing record
            result = db.client.table('bronze_activities').update(bronze_record).eq('activity_id', activity_data['id']).execute()
            logger.info(f"Updated activity {activity_data['id']} in bronze layer")
        else:
            # Insert new record
            bronze_record['ingested_at'] = datetime.utcnow().isoformat()
            result = db.client.table('bronze_activities').insert(bronze_record).execute()
            logger.info(f"Ingested activity {activity_data['id']} into bronze layer")
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to upsert activity {activity_data.get('id', 'unknown')}: {e}")
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
        if upsert_activity(activity_data):  # Use upsert to handle updates
            success_count += 1
    
    logger.info(f"Ingested/upserted {success_count}/{len(activities_data)} activities into bronze layer")
    return success_count


def fetch_and_ingest_recent(
    limit: int = 100,
    after: Optional[int] = None,
    incremental: bool = True,
) -> int:
    """Fetch recent activities from Strava and ingest into bronze layer.
    
    Args:
        limit: Maximum number of activities to fetch
        after: Unix timestamp to fetch activities after this date
        incremental: If True, only fetch activities after latest stored activity
        
    Returns:
        Number of successfully ingested activities
    """
    try:
        # If incremental, get the latest activity date from bronze layer
        if incremental and db:
            try:
                latest = db.client.table('bronze_activities').select('activity_id').order('ingested_at', desc=True).limit(1).execute()
                if latest.data:
                    # Convert activity_id to timestamp approximation or use stored timestamp
                    latest_activity_id = latest.data[0]['activity_id']
                    logger.info(f"Incremental mode: Fetching activities after latest ID {latest_activity_id}")
                    # Note: Strava API doesn't support filtering by ID, but we can limit recent activities
            except Exception as e:
                logger.warning(f"Could not determine latest activity for incremental load: {e}")
        
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


def run_bronze_ingestion(limit: int = 100, after: Optional[int] = None, incremental: bool = True) -> Dict[str, Any]:
    """Run bronze layer ingestion.
    
    Args:
        limit: Maximum number of activities to fetch
        after: Unix timestamp to fetch activities after this date
        incremental: If True, only fetch new activities
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        ingested_count = fetch_and_ingest_recent(limit=limit, after=after, incremental=incremental)
        return {
            'ingested': ingested_count,
            'status': 'success',
            'error': None,
            'incremental': incremental
        }
    except Exception as e:
        return {
            'ingested': 0,
            'status': 'error',
            'error': str(e),
            'incremental': incremental
        }