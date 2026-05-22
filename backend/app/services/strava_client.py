"""Strava API client for fetching activity data."""
import time
import requests
from typing import Optional, List, Dict, Any
from loguru import logger
from app.config import settings
import datetime


class StravaClient:
    """Client for interacting with Strava API."""
    
    BASE_URL = "https://www.strava.com/api/v3"
    # Unix timestamp for January 1, 2026 00:00:00 UTC
    DEFAULT_AFTER_TIMESTAMP = int(datetime.datetime(2026, 1, 1).timestamp())
    
    def __init__(self):
        """Initialize Strava client with credentials from settings."""
        self.client_id = settings.STRAVA_CLIENT_ID
        self.client_secret = settings.STRAVA_CLIENT_SECRET
        self.refresh_token = settings.STRAVA_REFRESH_TOKEN
        self.access_token = settings.STRAVA_ACCESS_TOKEN
        self.token_expires_at = 0
    
    def refresh_access_token(self) -> str:
        """Refresh the access token using refresh token.
        
        Returns:
            New access token
        """
        try:
            response = requests.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=30,
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_at = token_data["expires_at"]
            
            logger.info("Successfully refreshed Strava access token")
            return self.access_token
        except requests.RequestException as e:
            logger.error(f"Failed to refresh Strava token: {e}")
            raise
    
    def get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token
        """
        current_time = int(time.time())
        if current_time >= self.token_expires_at - 300:  # Refresh 5 minutes before expiry
            return self.refresh_access_token()
        return self.access_token
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make an authenticated request to Strava API.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            data: Request body data
            retry_count: Current retry attempt
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.get_valid_access_token()}",
            "Content-Type": "application/json",
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                
                if retry_count < settings.ETL_RETRY_ATTEMPTS:
                    return self._make_request(endpoint, method, params, data, retry_count + 1)
                else:
                    raise Exception("Max retry attempts reached due to rate limiting")
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Strava API request failed: {e}")
            if retry_count < settings.ETL_RETRY_ATTEMPTS:
                logger.info(f"Retrying... (attempt {retry_count + 1}/{settings.ETL_RETRY_ATTEMPTS})")
                time.sleep(settings.ETL_RETRY_DELAY)
                return self._make_request(endpoint, method, params, data, retry_count + 1)
            raise
    
    def get_activity(self, activity_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific activity.
        
        Args:
            activity_id: Strava activity ID
            
        Returns:
            Activity data from Strava API
        """
        logger.info(f"Fetching activity {activity_id} from Strava API")
        return self._make_request(f"activities/{activity_id}")
    
    def get_activities(
        self,
        per_page: int = 100,
        page: int = 1,
        after: Optional[int] = None,
        before: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of athlete activities.
        
        Args:
            per_page: Number of activities per page (max 200)
            page: Page number
            after: Unix timestamp for start date filter
            before: Unix timestamp for end date filter
            
        Returns:
            List of activities
        """
        logger.info(f"Fetching activities page {page} from Strava API")
        params = {
            "per_page": min(per_page, 200),
            "page": page,
        }
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        
        return self._make_request("athlete/activities", params=params)
    
    def get_all_activities(
        self,
        after: Optional[int] = None,
        before: Optional[int] = None,
        max_activities: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get all athlete activities with pagination.
        
        Args:
            after: Unix timestamp for start date filter (defaults to Jan 1, 2026)
            before: Unix timestamp for end date filter
            max_activities: Maximum number of activities to fetch
            
        Returns:
            List of all activities
            
        Raises:
            Exception: If Strava API request fails
        """
        # Default to 2026 onwards if no after parameter provided
        if after is None:
            after = self.DEFAULT_AFTER_TIMESTAMP
            logger.info(f"Fetching activities from 2026 onwards (after={after})")
        
        all_activities = []
        page = 1
        
        while True:
            activities = self.get_activities(per_page=200, page=page, after=after, before=before)
            
            if not activities:
                break
            
            all_activities.extend(activities)
            
            if max_activities and len(all_activities) >= max_activities:
                all_activities = all_activities[:max_activities]
                break
            
            page += 1
            logger.info(f"Fetched {len(all_activities)} activities so far")
        
        logger.info(f"Total activities fetched from Strava: {len(all_activities)}")
        return all_activities
    

    def get_athlete(self) -> Dict[str, Any]:
        """Get athlete profile information.
        
        Returns:
            Athlete data from Strava API
        """
        logger.info("Fetching athlete profile from Strava API")
        return self._make_request("athlete")
    
    def get_activity_streams(self, activity_id: int, types: List[str]) -> Dict[str, Any]:
        """Get activity streams (detailed data like time, latlng, etc).
        
        Args:
            activity_id: Strava activity ID
            types: List of stream types to retrieve (e.g., ["time", "latlng", "altitude"])
            
        Returns:
            Stream data dictionary
        """
        logger.info(f"Fetching streams for activity {activity_id}")
        params = {"keys": ",".join(types), "key_by_type": "true"}
        return self._make_request(f"activities/{activity_id}/streams", params=params)
    
    def create_subscription(
        self,
        callback_url: str,
        verify_token: str,
    ) -> Dict[str, Any]:
        """Create a webhook subscription.
        
        Args:
            callback_url: URL for Strava to send webhook events
            verify_token: Token for verifying webhook requests
            
        Returns:
            Subscription data
        """
        logger.info(f"Creating Strava webhook subscription for {callback_url}")
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "callback_url": callback_url,
            "verify_token": verify_token,
        }
        return self._make_request("push_subscriptions", method="POST", data=data)
    
    def view_subscriptions(self) -> List[Dict[str, Any]]:
        """View existing webhook subscriptions.
        
        Returns:
            List of subscriptions
        """
        logger.info("Viewing Strava webhook subscriptions")
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        return self._make_request("push_subscriptions", params=params)
    
    def delete_subscription(self, subscription_id: int) -> Dict[str, Any]:
        """Delete a webhook subscription.
        
        Args:
            subscription_id: Subscription ID to delete
            
        Returns:
            Response data
        """
        logger.info(f"Deleting Strava webhook subscription {subscription_id}")
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        return self._make_request(f"push_subscriptions/{subscription_id}", method="DELETE", params=params)


# Global instance
strava_client = StravaClient()
