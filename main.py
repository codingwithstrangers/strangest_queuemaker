import twitchio
import asyncio
from twitchio.ext import commands, pubsub
from configuration import *
import json
from datetime import datetime
import spotipy
import refresh_token
from spotipy.oauth2 import SpotifyClientCredentials
from cws_songs import regular_cws_songs, dlc_cws_songs
import threading
import time  # Importing the time module

# Setup Spotify API authentication
client_id = SPOTIFY_CLIENT_ID
client_secret = SPOTIFY_CLIENT_SECRET

def authenticate_spotify():
    credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=credentials)
    print("The music is in")  # Print statement when connected
    return sp

def get_song_length(sp, artist, song):
    results = sp.search(q=f'artist:{artist} track:{song}', type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]  # Get the first matching track
        return track['duration_ms'] / 1000  # Return length in seconds
    return 191  # Return default length of 3 minutes and 11 seconds

def format_time(seconds):
    """Convert seconds to H:MM:SS format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Function to export sorted user profiles to JSON
def export_to_json():
    # Sort user profiles by priority (True comes before False), maintaining the order of entry for each group
    sorted_profiles = {user: profile for user, profile in sorted(users_profiles.items(), key=lambda item: (not item[1]['priority'], item[1]['time']))}

    with open('user_profiles.json', 'w') as f:
        json.dump(sorted_profiles, f, indent=4)  # Export sorted profiles to JSON

# Dictionary to store user profiles
users_profiles = {}

user_token = USER_TOKEN
oauth_token = CLIENT_ID
broadcaster_id = int(BROADCASTER_ID)
broadcast_name = CHANNEL_NAME

client = twitchio.Client(token=user_token)
client.pubsub = pubsub.PubSubPool(client)

# Run refresh before code
refresh_token.refresh_access_token()

# Authenticate Spotify
sp = authenticate_spotify()

# Timer variables
current_time = 5800  # Default start time in seconds
countdown_running = True

def update_timer_file():
    with open('song_timer.txt', 'w') as f:
        f.write(str(current_time))  # Write the current time to the file

def start_count():
    global current_time, countdown_running
    print("Countdown started...")
    while current_time > 0 and countdown_running:
        formatted_time = format_time(current_time)  # Format the time
        print(f"Current countdown: {formatted_time}")  # Display countdown
        update_timer_file()  # Update the txt file with the current countdown
        time.sleep(1)  # Wait for 1 second
        current_time -= 1

    if current_time <= 0:
        print("Countdown finished.")

def add_time_to_count(song_length):
    global current_time
    current_time += song_length  # Add song length to current time

# Start the countdown in a separate thread
countdown_thread = threading.Thread(target=start_count)
countdown_thread.start()

# Event for handling bit redemptions
@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    user_name = event.user.name
    amount = event.bits_used
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = event.message if hasattr(event, "message") else "NA"
    print(f"Bits received: {event.bits_used} from {event.user.name}")

    # Check if message contains CWS keys
    cws_number = ""
    song_info = {}
    dict_source = None
    # Make sure sentnce is a string 
    if isinstance(message,str):
        message_lower = message.lower()
    else:
        message_lower = ""
    
      # Convert message to lowercase

    # Check for CWS in regular songs
    for key in regular_cws_songs.keys():
        if key.lower() in message_lower:
            song_info = regular_cws_songs[key]
            cws_number = key.lower()
            dict_source = "regular"
            print('Song was Found')
            break  
        
        else:
            print('Regular songs checked not found')

    print(key)
    print(cws_number)

    # Check for CWS in DLC songs if not found in regular
    if not cws_number:
        for key in dlc_cws_songs.keys():
            if key.lower() in message_lower:
                song_info = dlc_cws_songs[key]
                cws_number = key.lower()
                dict_source = "dlc"
                print('Song was Found')
            break  
        
        else:
            print('Regular songs checked not found')
            
    print(key)
    print(cws_number)
   
    if cws_number:
        # Get song length, default to 191 seconds if not found
        song_length = get_song_length(sp, song_info["artist"], song_info["song"])

        # Create user profile based on amount and song source
        if dict_source == "regular" and amount < 1:
            return  # Don't create profile for regular song under 100 bits
        elif 3 <= amount < 5:
            priority = False  # Less than 500, priority is false
            if dict_source == "regular":
                return  # Skip if regular song under 100 bits
        elif amount >= 500:
            priority = True  # Priority for 500 bits or more
        else:
            priority = False  # Default priority for other cases
        print('song checked')

        # Construct user profile
        users_profiles[user_name] = {
            "amount": amount,
            "time": time,
            "message": message,
            "cws_number": cws_number,
            "song": song_info["song"],
            "artist": song_info["artist"],
            "cws_source": dict_source,
            "cws": True,
            "priority": priority,
            "length": song_length  # Add the length to the user profile
        }

        # Add the song length to the current countdown
        add_time_to_count(song_length)

        # Export updated profiles to JSON
        export_to_json()

        # Adding  commands to let bit user know song was added
        channel = client.get_channel(broadcast_name)
        await channel.send(f"coding32Newheart @{user_name}, your request has been added, thanks for the support!")

async def main():
    # Define the topics to subscribe to
    topics = [
        pubsub.bits(user_token)[broadcaster_id],
    ]
    
    # Subscribe to the defined topics
    await client.pubsub.subscribe_topics(topics)
    
    # Start the client
    await client.start()

# Run the main function
if __name__ == "__main__":
    client.loop.run_until_complete(main())
