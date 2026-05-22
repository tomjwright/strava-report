"""
Strava OAuth Authorization Script

This script helps you re-authorize the Strava application to get fresh access tokens.
Follow the instructions to authorize the application and update your .env file.
"""

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests
import os
from pathlib import Path

# Your Strava API credentials
CLIENT_ID = "249256"
CLIENT_SECRET = "96af13f3695346651a76fd82e646f7de2be91510"

# OAuth configuration
REDIRECT_URI = "http://localhost:8080/callback"
AUTHORIZATION_SCOPE = "activity:read_all"
PORT = 8080

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback from Strava"""
    
    authorization_code = None
    
    def do_GET(self):
        if '/callback' in self.path:
            # Parse the authorization code from the callback URL
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                OAuthCallbackHandler.authorization_code = params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <p>The script will automatically exchange the authorization code for access tokens.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            else:
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Error: No authorization code received</h1></body></html>")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass


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
    print("Strava OAuth Authorization Setup")
    print("=" * 60)
    print(f"\nClient ID: {CLIENT_ID}")
    print(f"Client Secret: {CLIENT_SECRET[:20]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Requested Scope: {AUTHORIZATION_SCOPE}")
    
    # Start local server to handle callback
    print(f"\nStarting local server on port {PORT}...")
    server = HTTPServer(('localhost', PORT), OAuthCallbackHandler)
    
    # Build authorization URL
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={AUTHORIZATION_SCOPE}"
        f"&approval_prompt=auto"
    )
    
    print(f"\n1. Opening your browser to authorize the application...")
    print(f"   Authorization URL: {auth_url}")
    
    # Open browser for authorization
    webbrowser.open(auth_url)
    
    print(f"\n2. Please authorize the application in your browser.")
    print(f"   After authorization, you will be redirected to {REDIRECT_URI}")
    print(f"   The script will automatically capture the authorization code.")
    
    # Wait for callback (with timeout)
    print("\n3. Waiting for authorization callback...")
    server.timeout = 120  # 2 minute timeout
    
    try:
        server.handle_request()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Authorization process cancelled by user")
        server.shutdown()
        return
    
    # Check if we got the authorization code
    if OAuthCallbackHandler.authorization_code:
        print(f"[SUCCESS] Received authorization code: {OAuthCallbackHandler.authorization_code[:20]}...")
        
        # Exchange code for tokens
        token_data = exchange_code_for_tokens(OAuthCallbackHandler.authorization_code)
        
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
    else:
        print("\n[ERROR] Failed to receive authorization code")
        print("Please try running the script again.")
    
    # Shutdown server
    server.shutdown()


if __name__ == "__main__":
    main()
