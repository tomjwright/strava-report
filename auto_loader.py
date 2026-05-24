"""Automated daily Strava data loader."""
import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def load_strava_data():
    """Run the data loader script."""
    logger.info("Starting scheduled Strava data load...")
    try:
        result = subprocess.run(
            ['python', 'simple_data_loader.py'],
            cwd='C:/workspace/strava-report',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Data loaded successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"Data load failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Error running data loader: {e}")

def main():
    """Main scheduler."""
    logger.info("Strava Auto-Loader Started")
    logger.info("Scheduled to run daily at 6:00 AM")
    
    # Schedule daily at 6:00 AM
    schedule.every().day.at("06:00").do(load_strava_data)
    
    # Run once immediately on startup
    logger.info("Running initial data load...")
    load_strava_data()
    
    # Keep the script running
    logger.info("Scheduler running, waiting for next scheduled run...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()