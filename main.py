import twitchio
import asyncio
from twitchio.ext import pubsub
from configuration import *
from datetime import datetime

class Get_Access:
    def __init__(self):     
        self.user_token = USER_TOKEN
        self.oauth_token = CLIENT_ID
        self.broadcaster_id = int(BROADCASTER_ID)

    def verify_token(self):
        twitch_ready = self.user_token and self.oauth_token and self.broadcaster_id
        if twitch_ready:
            print("Twitch tokens are ready to go!")
            return True
        else:
            print("Error: One or more Twitch tokens are missing.")
            return False


class User_Builder:
    def __init__(self, access):
        self.access = access
        self.client = twitchio.Client(token=self.access.user_token)
        self.client.pubsub = pubsub.PubSubPool(self.client)
        self.user_profiles = {}

    # Building twitchio user subscribe event
    async def build_user(self):
        if self.access.verify_token():
            print('User_Builder has access to Twitch client')
            await self.subscribe_to_events()
            await self.client.start()

    async def subscribe_to_events(self):
        topics = [
            pubsub.channel_points(self.access.oauth_token)[self.access.broadcaster_id],
            pubsub.bits(self.access.oauth_token)[self.access.broadcaster_id]
        ]
        await self.client.pubsub.subscribe_topics(topics)
        print('Subscribed to topics')

    # Event handler for bits redemptions
    async def event_pubsub_bits(self, event: pubsub.PubSubBitsMessage):
        print('Received bits event')
        print(f'Bits Amount: {event.bits_used}, User: {event.user.name if event.user else "Anonymous"}')

        # Store your data
        user_name = event.user.name if event.user else "Stranger"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
        
        # Add user to the profile dictionary
        self.user_profiles[user_name] = {
            'bit_used': event.bits_used,
            'message': event.message,
            'channel_id': event.channel_id,
            'timestamp': timestamp
        }
        print(f'Updated user profiles: {self.user_profiles}')


class Bot:
    def __init__(self):
        self.access_manager = Get_Access()  # Manage access tokens
        self.user_builder = User_Builder(self.access_manager)  # Manage Twitch client and subscriptions

    async def run(self):
        print("Bot is starting...")
        await self.user_builder.build_user()

    def start(self):
        # Launch the bot asynchronously and handle manual exit
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            print("Bot was stopped manually.")


if __name__ == "__main__":
    bot = Bot()
    bot.start()
