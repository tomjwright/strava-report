"""
Master ETL Orchestrator - Runs complete medallion architecture pipeline
Bronze → Silver → Gold transformation with error handling and monitoring
"""
from typing import Dict, Any
from loguru import logger

from app.etl.bronze import run_bronze_ingestion
from app.etl.silver import run_silver_transformation
from app.etl.gold import run_gold_transformation
from app.db.supabase_adapter import db


def run_full_etl_pipeline(
    bronze_limit: int = 100,
    silver_limit: int = 100,
    gold_limit: int = 100,
    after_timestamp: int = None,
    incremental: bool = True
) -> Dict[str, Any]:
    """Run the complete ETL pipeline: Bronze → Silver → Gold.
    
    Args:
        bronze_limit: Max activities to fetch from Strava
        silver_limit: Max activities to transform to silver
        gold_limit: Max activities to transform to gold
        after_timestamp: Unix timestamp for incremental loading
        incremental: Whether to run in incremental mode
        
    Returns:
        Dictionary with pipeline execution results
    """
    pipeline_start = logger.info("Starting complete ETL pipeline: Bronze → Silver → Gold")
    
    results = {
        'bronze': None,
        'silver': None,
        'gold': None,
        'overall_status': 'success',
        'errors': []
    }
    
    try:
        # Step 1: Bronze Layer - Fetch raw Strava data
        logger.info("=" * 60)
        logger.info("STEP 1: BRONZE LAYER - Fetching raw Strava data")
        logger.info("=" * 60)
        
        bronze_result = run_bronze_ingestion(
            limit=bronze_limit,
            after=after_timestamp,
            incremental=incremental
        )
        results['bronze'] = bronze_result
        
        if bronze_result['status'] != 'success':
            error_msg = f"Bronze layer failed: {bronze_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['overall_status'] = 'failed'
            return results
        
        logger.info(f"✅ Bronze layer completed: {bronze_result['ingested']} activities ingested")
        
        # Step 2: Silver Layer - Transform to cleaned data
        logger.info("=" * 60)
        logger.info("STEP 2: SILVER LAYER - Transforming to cleaned data")
        logger.info("=" * 60)
        
        silver_result = run_silver_transformation(
            limit=silver_limit,
            incremental=incremental
        )
        results['silver'] = silver_result
        
        if silver_result['status'] != 'success':
            error_msg = f"Silver layer failed: {silver_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['overall_status'] = 'partial'  # Continue to gold layer
        else:
            logger.info(f"✅ Silver layer completed: {silver_result['transformed']} activities transformed")
        
        # Step 3: Gold Layer - Transform to dimensional model
        logger.info("=" * 60)
        logger.info("STEP 3: GOLD LAYER - Transforming to dimensional model")
        logger.info("=" * 60)
        
        gold_result = run_gold_transformation(
            limit=gold_limit,
            incremental=incremental
        )
        results['gold'] = gold_result
        
        if gold_result['status'] != 'success':
            error_msg = f"Gold layer failed: {gold_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['overall_status'] = 'partial'
        else:
            logger.info(f"✅ Gold layer completed: {gold_result['transformed']} activities transformed")
        
        # Pipeline summary
        logger.info("=" * 60)
        logger.info("ETL PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Bronze: {bronze_result['ingested']} activities")
        logger.info(f"Silver: {silver_result['transformed'] if silver_result else 0} activities")
        logger.info(f"Gold: {gold_result['transformed'] if gold_result else 0} activities")
        logger.info(f"Overall Status: {results['overall_status'].upper()}")
        
        if results['errors']:
            logger.warning(f"Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        logger.info("ETL pipeline completed")
        
        return results
        
    except Exception as e:
        error_msg = f"Pipeline execution failed: {str(e)}"
        logger.error(error_msg)
        results['overall_status'] = 'failed'
        results['errors'].append(error_msg)
        return results


def run_health_check() -> Dict[str, Any]:
    """Run health check on ETL pipeline components.
    
    Returns:
        Dictionary with health check results
    """
    health_status = {
        'database': False,
        'strava_api': False,
        'tables': {
            'bronze.bronze_activities': False,
            'silver.silver_activities': False,
            'gold.dim_activity_type': False,
            'gold.dim_date': False,
            'gold.fact_activities': False,
            'gold.fact_daily_summary': False
        },
        'overall_status': 'unhealthy'
    }
    
    try:
        # Check database connection
        if db:
            health_status['database'] = True
            logger.info("✅ Database connection healthy")
        else:
            logger.error("❌ Database connection failed")
        
        # Check Strava API
        try:
            from app.services.strava_client import strava_client
            strava_client.get_valid_access_token()
            health_status['strava_api'] = True
            logger.info("✅ Strava API connection healthy")
        except Exception as e:
            logger.error(f"❌ Strava API connection failed: {e}")
        
        # Check table existence
        if db:
            for table in health_status['tables']:
                try:
                    db.client.table(table).select('*').limit(1).execute()
                    health_status['tables'][table] = True
                    logger.info(f"✅ Table {table} exists")
                except Exception as e:
                    logger.warning(f"⚠️ Table {table} not accessible: {e}")
        
        # Determine overall status
        all_healthy = all([
            health_status['database'],
            health_status['strava_api'],
            all(health_status['tables'].values())
        ])
        
        health_status['overall_status'] = 'healthy' if all_healthy else 'degraded'
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status['overall_status'] = 'unhealthy'
    
    return health_status