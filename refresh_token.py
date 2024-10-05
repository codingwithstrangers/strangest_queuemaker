import requests
import json
import asyncio
from dotenv import load_dotenv, set_key
import os

# Load the existing environment variables from .env file
load_dotenv()

# Replace these with actual keys from .env
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

# Endpoint to refresh the OAuth token
TOKEN_URL = "https://id.twitch.tv/oauth2/token"

# Function to refresh the token
def refresh_access_token():
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    response = requests.post(TOKEN_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        new_access_token = data['access_token']
        new_refresh_token = data.get('refresh_token', REFRESH_TOKEN)  # In case Twitch provides a new refresh token

        # Update .env file with new tokens
        update_tokens(new_access_token, new_refresh_token)

        print(f"Access token refreshed")
        return new_access_token
    else:
        print(f"Failed to refresh token: {response.text}")
        return None

# Function to update .env with new tokens
def update_tokens(access_token, refresh_token):
    env_file = '.env'
    # Set the new access token and refresh token
    set_key(env_file, "USER_TOKEN", access_token)
    set_key(env_file, "REFRESH_TOKEN", refresh_token)

# Async function to refresh token every 3 hours and 3 mins
async def toke_refresh_loop():
    while True:
        refresh_access_token()
        await asyncio.sleep(12600)


if __name__ == "__main__":
    refresh_access_token()
