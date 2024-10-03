import twitchio
import asyncio
from twitchio.ext import pubsub
from configuration import *

users_token = USER_TOKEN
users_oauth_token = CLIENT_ID
users_channel_id = int(BROADCASTER_ID)
client = twitchio.Client(token=users_token)
client.pubsub = pubsub.PubSubPool(client)
topic = pubsub.bits(users_token)[users_channel_id]

# Event handler for bits redemptions
@client.event
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    print('Received bits event')  # Debug message to confirm event is triggered
    print(f'Bits Amount: {event.bits}, User: {event.user.name}')

# Main function to subscribe to topics
async def main():
    topics = [
        pubsub.channel_points(users_oauth_token)[users_channel_id],
        pubsub.bits(users_oauth_token)[users_channel_id]
    ]
    await client.pubsub.subscribe_topics(topics)
    print("Subscribed to topics")  # Debug message to confirm subscription
    await client.start()

client.loop.run_until_complete(main())
