import twitchio
import asyncio
from twitchio.ext import commands, pubsub
from configuration import *
import json
import re
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

class SongTimer:
    def __init__(self, start_time=5800):
        self.current_time = start_time  # Timer starts at a default value (5800 seconds)
        self.countdown_running = False  # Control the countdown
        self.timer_thread = None  # Placeholder for the timer thread

    def update_timer_file(self):
        with open('song_timer.txt', 'w') as f:
            f.write(str(self.current_time))  # Write the current time to the file

    def start_count(self):
        self.countdown_running = True
        print("Countdown started...")
        while self.current_time > 0 and self.countdown_running:
            formatted_time = self.format_time(self.current_time)  # Format the time
            print(f"Current countdown: {formatted_time}")  # Display countdown
            self.update_timer_file()  # Update the txt file with the current countdown
            time.sleep(1)  # Wait for 1 second
            self.current_time -= 1

        if self.current_time <= 0:
            print("Countdown finished.")

    def add_time_to_count(self, song_length):
        self.current_time += song_length  # Add song length to current time

    def format_time(self, seconds):
        hours, seconds = divmod(seconds, 3600)  # Convert seconds to hours and remaining seconds
        minutes, seconds = divmod(seconds, 60)  # Convert remaining seconds to minutes and seconds
        return f"{int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds" 

    def reset_timer(self, new_time):
        self.current_time = new_time  # Reset the timer to a new value

    def start_timer(self):
        if not self.timer_thread or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.start_count)
            self.timer_thread.start()  # Start the countdown in a separate thread

# Initialize the SongTimer
song_timer = SongTimer()  # Create an instance of SongTimer
song_timer.start_timer()  # Start the countdown timer


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
user_queue = {}
# Event for handling bit redemptions
@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    user_name = event.user.name
    amount = event.bits_used
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = event.message.content 
    print(message)
    print(f"Bits received: {event.bits_used} from {event.user.name}")

    cws_number = ""
    song_info = {}
    dict_source = None

    match = re.search(r'cws_\d+', message, re.IGNORECASE)
    if match:
        cws_number = match.group().upper()  # Convert to uppercase for dictionary match
        print(f"Extracted CWS key: {cws_number}")

        # Check if the key exists in the DLC songs dictionary
        if cws_number in dlc_cws_songs:
            dict_source = "dlc"
            artist_name, song_title = dlc_cws_songs[cws_number]
            song_info = {"artist": artist_name, "song": song_title}
            
            # DLC songs require at least 300 bits, 500 or more for priority
            # Get song length from Spotify
            length = get_song_length(sp, song_info["artist"], song_info["song"])
            if amount >= 3:
                priority = amount >= 5  # True if 500 bits or more, otherwise False
                print(f"Adding {cws_number} (DLC) to user queue. Priority: {priority}")
                # Add to user_queue
                user_queue[user_name] = {
                    "amount": amount,
                    "time": time,
                    "message": message,
                    "cws_number": cws_number,
                    "song": song_info["song"],
                    "artist": song_info["artist"],
                    "cws_source": dict_source,
                    "priority": priority,
                    "length": length,
                }
                song_timer.add_time_to_count(length)  # Add song length to the timer
            elif 1 <= amount < 3:
                print(f"Hey {user_name}, you might want to try a regular song for that donation.")

        # Check if the key exists in the regular songs dictionary
        elif cws_number in regular_cws_songs:
            dict_source = "regular"
            artist_name, song_title = regular_cws_songs[cws_number]
            song_info = {"artist": artist_name, "song": song_title}

            # Get song length from Spotify
            length = get_song_length(sp, song_info["artist"], song_info["song"])
            # Regular songs require at least 100 bits, 500 or more for priority
            if amount >= 1:
                priority = amount >= 5  # True if 500 bits or more, otherwise False
                print(f"Adding {cws_number} (Regular) to user queue. Priority: {priority}")
                # Add to user_queue
                user_queue[user_name] = {
                    "amount": amount,
                    "time": time,
                    "message": message,
                    "cws_number": cws_number,
                    "song": song_info["song"],
                    "artist": song_info["artist"],
                    "cws_source": dict_source,
                    "priority": priority,
                    "length": length,
                }
                song_timer.add_time_to_count(length)  # Add song length to the timer
            else:
                print(f"Hey {user_name}, get they money up not they funny up.")

        # If the CWS key was not found in either dictionary
        else:
            print(f"{cws_number} not found in either dictionary.")
    
    # No CWS key in the message
    else:
        print(f"No CWS number found in the message: {message}")

    # Update user_profiles.json
    update_user_profiles(user_queue)

def update_user_profiles(user_queue):
    """Update the user_profiles.json file based on current user queue."""
    user_profiles = []

    for user_name, profile in user_queue.items():
        user_profiles.append({
            "user_name": user_name,
            "song": profile["song"],
            "amount": profile["amount"],
            "priority": profile["priority"],
            "cws_source": profile["cws_source"],
            "length_mins": profile["length"] / 60  # Convert seconds to minutes
        })

    # Sort the user profiles
    user_profiles.sort(key=lambda x: (not x['priority'], x['amount']), reverse=True)

    # Clear the file and write updated profiles
    with open('user_profiles.json', 'w') as f:
        json.dump(user_profiles, f, indent=4)  # Save to JSON file
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