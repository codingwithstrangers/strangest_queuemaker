import requests
import json
import asyncio
from configuration import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

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

        # Update configuration with new tokens
        update_tokens(new_access_token, new_refresh_token)

        print(f"Access token refreshed: {new_access_token}")
        return new_access_token
    else:
        print(f"Failed to refresh token: {response.text}")
        return None

# Function to update configuration.py with new tokens
def update_tokens(access_token, refresh_token):
    with open('configuration.py', 'r') as file:
        config_data = file.readlines()

    with open('configuration.py', 'w') as file:
        for line in config_data:
            if line.startswith("USER_TOKEN"):
                file.write(f"USER_TOKEN = '{access_token}'\n")
            elif line.startswith("REFRESH_TOKEN"):
                file.write(f"REFRESH_TOKEN = '{refresh_token}'\n")
            else:
                file.write(line)

# Aysnc function to refresh token every 3hours and 3mins
async def toke_refresh_loop():
    while True:
        refresh_access_token
        await asyncio.sleep(12600)

# Main function 
async def main():
    asyncio.create_task(toke_refresh_loop()) 
    # Here we can start twitch client again
    access_manager = Get_Access()
    user_builder = User_Builder(access_manager)
    await user_builder.build_user()

if __name__ == "__main__":
    refresh_access_token()
