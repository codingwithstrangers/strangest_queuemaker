import twitchio
import asyncio
from twitchio.ext import commands, pubsub
from configuration import *
import json
from datetime import datetime
import re
import spotipy
import refresh_token
from spotipy.oauth2 import SpotifyClientCredentials
from cws_songs import regular_cws_songs, dlc_cws_songs
import threading
import time

# Setup Spotify API authentication
# client_id = SPOTIFY_CLIENT_ID
# client_secret = SPOTIFY_CLIENT_SECRET

# credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
# sp = spotipy.Spotify(client_credentials_manager=credentials)

# def get_song_length(song_name, artist_name):
#     """Fetch the song length from Spotify based on song name and artist."""
#     query = f"track:{song_name} artist:{artist_name}"
#     results = sp.search(q=query, type='track', limit=1)
    
#     if results['tracks']['items']:
#         track = results['tracks']['items'][0]
#         return track['duration_ms'] / 1000  # Duration in seconds
#     return 180  # Default to 3 minutes (180 seconds) if not found

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

# Mock user profile
test_users_profiles = {
    "TestUser1": {
        "amount": 500,  # Mock bit donation
        "time": "2024-10-08 14:30:00",
        "message": "I want to hear CWS_40",
        "cws_number": "cws_175",
        "song": "Castles Made of Sand",
        "artist": "Jimi Hendrix",
        "cws_source": "regular",  # Could be "regular" or "dlc"
        "priority": None,
        "length": 191  # Song length in seconds
    }
}

user_queue = {}

def process_mock_donation(user_profile):
    user_name = user_profile.get("user_name", "TestUser")
    amount = user_profile.get("amount", 0)
    time = user_profile.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = user_profile.get("message", "")
    
    # Check if message contains a CWS key (case-insensitive)
    match = re.search(r'cws_\d+', message, re.IGNORECASE)
    if match:
        cws_number = match.group().upper()  # Convert to uppercase for dictionary match
        print(f"Extracted CWS key: {cws_number}")

        # Check if the key exists in the DLC songs dictionary
        if cws_number in dlc_cws_songs:
            dict_source = "dlc"
            song_info = {
                "song": dlc_cws_songs[cws_number][1],
                "artist": dlc_cws_songs[cws_number][0]
            }
            # DLC songs require at least 300 bits, 500 or more for priority
            # Get song length from Spotify
            length = 300
            if amount >= 300:
                priority = amount >= 500  # True if 500 bits or more, otherwise False
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
            elif 100 <= amount < 300:
                print(f"Hey {user_name}, you might want to try a regular song for that donation.")

        # Check if the key exists in the regular songs dictionary
        elif cws_number in regular_cws_songs:
            dict_source = "regular"
            song_info = regular_cws_songs[cws_number]
            # Get song length from Spotify
            length = 300
            # Regular songs require at least 100 bits, 500 or more for priority
            if amount >= 100:
                priority = amount >= 500  # True if 500 bits or more, otherwise False
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
                print(f"Hey {user_name}, get yea money up not yea funny up.")

        # If the CWS key was not found in either dictionary
        else:
            print(f"{cws_number} not found in either dictionary.")
    
    # No CWS key in the message
    else:
        print(f"No CWS number found in the message: {message}")

    # Update user_profiles.json
    update_user_profiles(user_queue)
    return user_queue

    #update the user data time 
def convert_length_to_minutes(length_seconds):
    """Convert length from seconds to minutes."""
    return length_seconds / 60  # Convert seconds to minutes

    

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
            "length_mins": convert_length_to_minutes(profile["length"])
        })

    # Sort the user profiles
    user_profiles.sort(key=lambda x: (not x['priority'], x['amount']), reverse=True)

    # Clear the file and write updated profiles
    with open('user_profiles.json', 'w') as f:
        json.dump(user_profiles, f, indent=4)  # Save to JSON file

# Example usage with test user profile
updated_profile = process_mock_donation(test_users_profiles["TestUser1"])
print(f"Updated profile: {updated_profile}")
