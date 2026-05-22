"""Silver layer ETL: Transform bronze data to cleaned data using Supabase client."""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

from app.db.supabase_adapter import db


def clean_activity_data(raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Clean and validate raw activity data from bronze layer.
    
    Args:
        raw_data: Raw activity data from bronze layer
        
    Returns:
        Cleaned activity data or None if validation fails
    """
    try:
        # Extract and validate required fields
        activity_id = raw_data.get('id')
        if not activity_id:
            logger.warning(f"Activity missing required field 'id'")
            return None
        
        # Clean and standardize field names
        cleaned_data = {
            'activity_id': activity_id,
            'activity_name': raw_data.get('name', '').strip() or 'Untitled',
            'type': raw_data.get('type', 'Unknown').strip(),
            'sport_type': raw_data.get('sport_type', 'Unknown').strip(),
            
            # Numeric fields with validation
            'distance': float(raw_data.get('distance', 0) or 0),
            'moving_time': int(raw_data.get('moving_time', 0) or 0),
            'elapsed_time': int(raw_data.get('elapsed_time', 0) or 0),
            'total_elevation_gain': float(raw_data.get('total_elevation_gain', 0) or 0),
            'average_speed': float(raw_data.get('average_speed', 0) or 0),
            'max_speed': float(raw_data.get('max_speed', 0) or 0),
            
            # Timestamp fields
            'start_date': raw_data.get('start_date'),
            'start_date_local': raw_data.get('start_date_local'),
            'timezone': raw_data.get('timezone', 'UTC'),
            
            # Social metrics
            'achievement_count': int(raw_data.get('achievement_count', 0) or 0),
            'kudos_count': int(raw_data.get('kudos_count', 0) or 0),
            'comment_count': int(raw_data.get('comment_count', 0) or 0),
            'athlete_count': int(raw_data.get('athlete_count', 0) or 0),
            'photo_count': int(raw_data.get('photo_count', 0) or 0),
            
            # Boolean flags
            'trainer': bool(raw_data.get('trainer', False)),
            'commute': bool(raw_data.get('commute', False)),
            'manual': bool(raw_data.get('manual', False)),
            'private': bool(raw_data.get('private', False)),
            'flagged': bool(raw_data.get('flagged', False)),
            
            # Metadata
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Data quality checks
        if cleaned_data['moving_time'] <= 0:
            logger.warning(f"Activity {activity_id} has invalid moving_time: {cleaned_data['moving_time']}")
        
        if cleaned_data['distance'] < 0:
            logger.warning(f"Activity {activity_id} has invalid distance: {cleaned_data['distance']}")
            cleaned_data['distance'] = 0
        
        return cleaned_data
        
    except Exception as e:
        logger.error(f"Error cleaning activity {raw_data.get('id', 'unknown')}: {e}")
        return None


def upsert_silver_activity(activity_id: int) -> Optional[Dict[str, Any]]:
    """Transform and upsert a single activity from bronze to silver layer.
    
    Args:
        activity_id: Activity ID to transform
        
    Returns:
        Inserted/updated record or None if failed
    """
    try:
        if not db:
            logger.error("Database not available")
            return None
        
        # Get raw data from bronze layer
        bronze_result = db.client.table('bronze_activities').select('*').eq('activity_id', activity_id).execute()
        
        if not bronze_result.data:
            logger.warning(f"Activity {activity_id} not found in bronze layer")
            return None
        
        raw_data = bronze_result.data[0]['raw_data']
        
        # Clean the data
        cleaned_data = clean_activity_data(raw_data)
        if not cleaned_data:
            return None
        
        # Check if activity already exists in silver layer
        existing = db.client.table('silver_activities').select('*').eq('activity_id', activity_id).execute()
        
        if existing.data:
            # Update existing record
            result = db.client.table('silver_activities').update(cleaned_data).eq('activity_id', activity_id).execute()
            logger.info(f"Updated activity {activity_id} in silver layer")
        else:
            # Insert new record
            result = db.client.table('silver_activities').insert(cleaned_data).execute()
            logger.info(f"Inserted activity {activity_id} into silver layer")
            
        return result
        
    except Exception as e:
        logger.error(f"Error upserting silver activity {activity_id}: {e}")
        return None


def transform_new_bronze_to_silver(limit: int = 100) -> int:
    """Transform new activities from bronze to silver layer.
    
    Args:
        limit: Maximum number of activities to transform
        
    Returns:
        Number of successfully transformed activities
    """
    try:
        if not db:
            logger.error("Database not available")
            return 0
        
        logger.info(f"Transforming up to {limit} activities from bronze to silver layer")
        
        # Get activities from bronze layer that aren't in silver layer
        # This is a simple approach - in production you'd use a more sophisticated incremental strategy
        bronze_result = db.client.table('bronze_activities').select('*').order('ingested_at', desc=True).limit(limit).execute()
        
        if not bronze_result.data:
            logger.info("No activities found in bronze layer")
            return 0
        
        success_count = 0
        for bronze_activity in bronze_result.data:
            activity_id = bronze_activity['activity_id']
            if upsert_silver_activity(activity_id):
                success_count += 1
        
        logger.info(f"Transformed {success_count}/{len(bronze_result.data)} activities to silver layer")
        return success_count
        
    except Exception as e:
        logger.error(f"Error transforming bronze to silver: {e}")
        return 0


def run_silver_transformation(limit: int = 100, incremental: bool = True) -> Dict[str, Any]:
    """Run silver layer transformation from bronze to silver.
    
    Args:
        limit: Maximum number of activities to transform
        incremental: If True, only transform new activities
        
    Returns:
        Dictionary with transformation results
    """
    try:
        logger.info("Starting silver layer transformation")
        transformed_count = transform_new_bronze_to_silver(limit=limit)
        
        return {
            'transformed': transformed_count,
            'status': 'success',
            'error': None,
            'incremental': incremental
        }
        
    except Exception as e:
        logger.error(f"Silver layer transformation failed: {e}")
        return {
            'transformed': 0,
            'status': 'error',
            'error': str(e),
            'incremental': incremental
        }