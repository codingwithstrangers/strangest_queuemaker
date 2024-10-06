# import twitchio
# import asyncio
# from twitchio.ext import commands, pubsub
# from configuration import *
# import json
# from datetime import datetime
# import refresh_token
# from cws_songs import regular_cws_songs, dlc_cws_songs 

# # Dictionary to store user profiles
# users_profiles = {}

# user_token = USER_TOKEN
# oauth_token = CLIENT_ID
# broadcaster_id = int(BROADCASTER_ID)

# client = twitchio.Client(token=user_token)
# client.pubsub = pubsub.PubSubPool(client)

# #Run refresh before code
# refresh_token.refresh_access_token()

# # Event for handling bit redemptions
# @client.event()
# async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
#     user_name = event.user.name
#     amount = event.bits_used
#     time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     message = event.message if hasattr(event,"message") else "NA"
#     print(f"Bits received: {event.bits_used} from {event.user.name}")
#     # Here, you can add your logic to handle bit redemptions

#     # use the this key:value
#     users_profiles[user_name] = {
#         "amount": amount,
#         "time": time,
#         "message": message
#     }


# async def main():
#     # Define the topics to subscribe to
#     topics = [
#         pubsub.bits(user_token)[broadcaster_id],
        
#     ]
    
#     # Subscribe to the defined topics
#     await client.pubsub.subscribe_topics(topics)
    
#     # Start the client
#     await client.start()

# # Run the main function
# if __name__ == "__main__":
#     client.loop.run_until_complete(main())
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

# Dictionary to store user profiles
users_profiles = {}

user_token = USER_TOKEN
oauth_token = CLIENT_ID
broadcaster_id = int(BROADCASTER_ID)

client = twitchio.Client(token=user_token)
client.pubsub = pubsub.PubSubPool(client)

# Run refresh before code
refresh_token.refresh_access_token()

# Authenticate Spotify
sp = authenticate_spotify()

# Event for handling bit redemptions
@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    user_name = event.user.name
    amount = event.bits_used
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = event.message if hasattr(event, "message") else "NA"
    print(f"Bits received: {event.bits_used} from {event.user.name}")

    # Check if message contains CWS keys
    cws_number = None
    song_info = {}
    dict_source = None
    
    message_lower = message.lower()  # Convert message to lowercase

    # Check for CWS in regular songs
    for key in regular_cws_songs.keys():
        if key.lower() in message_lower:
            song_info = regular_cws_songs[key]
            cws_number = key
            dict_source = "regular"
            break

    # Check for CWS in DLC songs if not found in regular
    if not cws_number:
        for key in dlc_cws_songs.keys():
            if key.lower() in message_lower:
                song_info = dlc_cws_songs[key]
                cws_number = key
                dict_source = "dlc"
                break

    if cws_number:
        # Get song length, default to 191 seconds if not found
        song_length = get_song_length(sp, song_info["artist"], song_info["song"])

        # Create user profile based on amount and song source
        if dict_source == "regular" and amount < 100:
            return  # Don't create profile for regular song under 100 bits
        elif 300 <= amount < 500:
            priority = False  # Less than 500, priority is false
            if dict_source == "regular":
                return  # Skip if regular song under 100 bits
        elif amount >= 500:
            priority = True  # Priority for 500 bits or more
        else:
            priority = False  # Default priority for other cases

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
