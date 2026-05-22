"""
Strava OAuth Authorization Script (Simple Version)

This script helps you re-authorize the Strava application to get fresh access tokens.
This version uses a manual copy-paste approach which works better in terminal environments.
"""

import requests
import os
from pathlib import Path

# Your Strava API credentials
CLIENT_ID = "249256"
CLIENT_SECRET = "96af13f3695346651a76fd82e646f7de2be91510"

# OAuth configuration
REDIRECT_URI = "http://localhost/callback"
AUTHORIZATION_SCOPE = "activity:read_all"


def exchange_code_for_tokens(authorization_code):
    """Exchange authorization code for access and refresh tokens"""
    
    print("Exchanging authorization code for access tokens...")
    
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("\n[SUCCESS] Successfully obtained tokens from Strava!")
        print(f"   Access Token: {token_data['access_token'][:20]}...")
        print(f"   Refresh Token: {token_data['refresh_token'][:20]}...")
        print(f"   Expires At: {token_data['expires_at']}")
        return token_data
    else:
        print(f"\n[ERROR] Error exchanging code for tokens: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def update_env_file(token_data):
    """Update the .env file with new tokens"""
    
    env_path = Path(".env")
    backup_path = Path(".env.backup")
    
    # Create backup
    if env_path.exists():
        print(f"\nCreating backup of current .env file at {backup_path}")
        with open(env_path, 'r') as f:
            backup_path.write_text(f.read())
    
    # Read existing .env file
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add the token lines
    updated_lines = []
    token_keys = {
        'STRAVA_ACCESS_TOKEN': token_data['access_token'],
        'STRAVA_REFRESH_TOKEN': token_data['refresh_token'],
    }
    
    for line in lines:
        line_stripped = line.strip()
        if any(line_stripped.startswith(key + '=') for key in token_keys.keys()):
            # Skip old token lines, we'll add new ones
            continue
        updated_lines.append(line)
    
    # Add new token lines
    for key, value in token_keys.items():
        updated_lines.append(f"{key}={value}\n")
    
    # Write updated .env file
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"[SUCCESS] Updated {env_path} with new tokens")


def main():
    print("=" * 60)
    print("Strava OAuth Authorization Setup (Simple)")
    print("=" * 60)
    print(f"\nClient ID: {CLIENT_ID}")
    print(f"Client Secret: {CLIENT_SECRET[:20]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Requested Scope: {AUTHORIZATION_SCOPE}")
    
    # Build authorization URL
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={AUTHORIZATION_SCOPE}"
        f"&approval_prompt=auto"
    )
    
    print(f"\nStep 1: Open this URL in your browser:")
    print(f"   {auth_url}")
    
    print(f"\nStep 2: Authorize the application on Strava")
    print(f"   You will be redirected to a page that shows an error (this is expected)")
    print(f"   The authorization code will be in the URL after 'code='")
    
    print(f"\nStep 3: Copy the authorization code from the URL")
    print(f"   Example: http://localhost/callback?code=YOUR_CODE_HERE...")
    
    print(f"\nStep 4: Paste the authorization code below")
    authorization_code = input("\nEnter authorization code: ").strip()
    
    if not authorization_code:
        print("\n[ERROR] No authorization code provided")
        return
    
    print(f"[SUCCESS] Received authorization code: {authorization_code[:20]}...")
    
    # Exchange code for tokens
    token_data = exchange_code_for_tokens(authorization_code)
    
    if token_data:
        # Update .env file
        update_env_file(token_data)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Setup Complete!")
        print("=" * 60)
        print("\nYour .env file has been updated with fresh Strava tokens.")
        print("You can now fetch real activity data from Strava.")
        print("\nNote: Access tokens expire every 6 hours, but the refresh")
        print("token will be used automatically to get new tokens.")
    else:
        print("\n[ERROR] Failed to exchange authorization code for tokens")


if __name__ == "__main__":
    main()
