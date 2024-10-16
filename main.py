import twitchio
import asyncio
from twitchio.ext import commands, pubsub
from configuration import *
import json
import re
from datetime import datetime
import refresh_token
from cws_songs import regular_cws_songs, dlc_cws_songs
import threading
import time  # Importing the time module


#clear json
with open('user_profiles.json', 'w') as f:
    f.write("")  

# Function to export sorted user profiles to JSON
def export_to_json():
    # Sort user profiles by priority (True comes before False), maintaining the order of entry for each group
    sorted_profiles = {user: profile for user, profile in sorted(users_profiles.items(), key=lambda item: (not item[1]['priority'], item[1]['time']))}

    with open('user_profiles.json', 'w') as f:
        json.dump(sorted_profiles, f, indent=4)  # Export sorted profiles to JSON

class SongTimer:
    def __init__(self, start_time=18000):
        self.current_time = start_time  # Timer starts at a default value (5800 seconds)
        self.countdown_running = False  # Control the countdown
        self.timer_thread = None  # Placeholder for the timer thread

    def update_timer_file(self):
        with open('song_timer.txt', 'w') as f:
            f.write(str(self.format_time))  # Write the current time to the file

    def start_count(self):
        self.countdown_running = True
        print("Countdown started...")
        
        while self.current_time > 0 and self.countdown_running:
            self.update_timer_file()  # Update the txt file with the current countdown
            time.sleep(1)  # Wait for 1 second
            self.current_time -= 1    

        if self.current_time <= 0:
            print("Countdown finished.")

    def add_time_to_count(self, song_length):
        self.current_time += song_length  # Add song length to current time

    @property
    def format_time(self):
        hours, seconds = divmod(self.current_time, 3600)  # Convert seconds to hours and remaining seconds
        minutes, seconds = divmod(seconds, 60)  # Convert remaining seconds to minutes and seconds
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}" 
        
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
user_queue = {}
user_token = USER_TOKEN
oauth_token = CLIENT_ID
broadcaster_id = int(BROADCASTER_ID)
broadcast_name = CHANNEL_NAME
client = twitchio.Client(token=user_token)
client.pubsub = pubsub.PubSubPool(client)

   
    #first we need the check CWS_number in the message
def get_cws_number(message:str):
    #use match to check message
    match = re.search(r'cws_\d+', message, re.IGNORECASE)
    # $if statemte for work
    if match:
        return  match.group().upper()
    else:
        return ""
def get_song_info(cws_number: str, amount: int) -> dict:
    """Retrieve song info from either DLC or regular song dictionaries based on the CWS number."""
    if cws_number in dlc_cws_songs:
        return {
            "dict_source": "dlc",
            "song": dlc_cws_songs[cws_number][1],
            "artist": dlc_cws_songs[cws_number][0],
            "length": 300,
            "priority": amount >= 5  
        }
    elif cws_number in regular_cws_songs:
        return {
            "dict_source": "regular",
            "song": regular_cws_songs[cws_number]["song"],
            "artist": regular_cws_songs[cws_number]["artist"],
            "length": 300,
            "priority": amount >= 5  
        }
    return None

#rebuild class for json export
def add_song(user_name: str, amount: int, time: str, message: str, cws_number: str, song_info: dict):
    """Add the song to the user queue and adjust the song timer."""
    user_queue[user_name] = {
        "amount": amount,
        "time": time,
        "message": message,
        "cws_number": cws_number,
        "song": song_info["song"],
        "artist": song_info["artist"],
        "cws_source": song_info["dict_source"],
        "priority": song_info["priority"],
        "length": song_info["length"]
    }
    print(f"Adding {cws_number} ({song_info['dict_source']}) to user queue. Priority: {song_info['priority']}")
    #need to also add time to clock if this works
    song_timer.add_time_to_count(song_info["length"])

#remember you want to tell it what it cant do vs what you want it to do 
def check_donation(amount: int, song_info: dict, user_name: str) -> bool:
    """Validate the donation based on the song type and amount."""
    #basically a song that is DLC but the bit amount is lower than expected 
    if song_info["dict_source"] == "dlc" and amount < 3:
        print(f"Hey {user_name}, you might want to try a regular song for that donation.")
        return False
    elif song_info["dict_source"] == "regular" and amount < 1:
        print(f"Hey {user_name}, get they money up not they funny up.")
        return False
    return True

# Event for handling bit redemptions
def event_handler(event):
    """Main event handler for processing bits and adding songs to the queue."""
    user_name = event.user.name
    amount = event.bits_used
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = event.message.content

    print(message)
    print(f"Bits received: {amount} from {user_name}")

    cws_number = get_cws_number(message)
    
    if cws_number:
        print(f"Extracted CWS key: {cws_number}")
        song_info = get_song_info(cws_number, amount)

        if song_info:
            if check_donation(amount, song_info, user_name):
                add_song(user_name, amount, time, message, cws_number, song_info)
                update_user_profiles(user_queue) 
        else:
            print(f"{cws_number} not found in either dictionary.")
    else:
        print(f"No CWS number found in the message: {message}")

@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    #call fuction to handle pubsub_events
    event_handler(event)
  
def convert_length_to_minutes(length_seconds):
    """Convert length from seconds to minutes."""
    return length_seconds / 60 

def update_user_profiles(user_queue):
    """Update the user_profiles.json file based on current user queue."""
    try:
        with open('user_profiles.json', 'r') as f:
            user_profiles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
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

    # Clear the file and write updated profiles
    user_profiles.sort(key=lambda x: (not x['priority'], x['amount']), reverse=False)
    with open('user_profiles.json', 'w') as f:
        json.dump(user_profiles, f, indent=4)

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