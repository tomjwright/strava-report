"""
Test Strava API credentials to diagnose the issue
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")

print("Testing Strava API credentials...")
print(f"Client ID: {CLIENT_ID}")
print(f"Client Secret: {CLIENT_SECRET[:20]}...")
print(f"Refresh Token: {REFRESH_TOKEN[:20]}...")
print(f"Access Token: {ACCESS_TOKEN[:20]}...")

# Try to refresh the access token
print("\nAttempting to refresh access token...")
try:
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        print("\n[SUCCESS] Token refresh worked!")
        print(f"New Access Token: {token_data['access_token'][:20]}...")
        print(f"New Refresh Token: {token_data['refresh_token'][:20]}...")
        
        # Update the .env file with new tokens
        print("\nUpdating .env file with new tokens...")
        env_path = ".env"
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        updated_lines = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("STRAVA_ACCESS_TOKEN=") or line_stripped.startswith("STRAVA_REFRESH_TOKEN="):
                continue
            updated_lines.append(line)
        
        updated_lines.append(f"STRAVA_ACCESS_TOKEN={token_data['access_token']}\n")
        updated_lines.append(f"STRAVA_REFRESH_TOKEN={token_data['refresh_token']}\n")
        
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print("[SUCCESS] Updated .env file with new tokens")
    else:
        print("\n[ERROR] Token refresh failed")
        
except Exception as e:
    print(f"Exception during token refresh: {e}")

# Try to use the current access token
print("\nAttempting to use current access token...")
try:
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers,
        params={"per_page": 1, "page": 1},
        timeout=30,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
    
    if response.status_code == 200:
        print("\n[SUCCESS] Current access token works!")
    else:
        print("\n[ERROR] Current access token failed")
        
except Exception as e:
    print(f"Exception during API call: {e}")
