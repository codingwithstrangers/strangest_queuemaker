import twitchio
import asyncio
from twitchio.ext import commands, pubsub
from configuration import *
import json
from datetime import datetime

# Dictionary to store user profiles
users_profiles = {}

user_token = USER_TOKEN
oauth_token = CLIENT_ID
broadcaster_id = int(BROADCASTER_ID)

client = twitchio.Client(token=user_token)
client.pubsub = pubsub.PubSubPool(client)

# Event for handling bit redemptions
@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    user_name = event.user.name
    amount = event.bits_used
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = event.message if hasattr(event,"message") else "NA"
    print(f"Bits received: {event.bits_used} from {event.user.name}")
    # Here, you can add your logic to handle bit redemptions

    # use the this key:value
    users_profiles[user_name] = {
        "amount": amount,
        "time": time,
        "message": message
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