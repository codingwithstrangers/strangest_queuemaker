import os
import json
from dotenv import load_dotenv
load_dotenv()

USER_TOKEN = os.environ['USER_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET= os.environ['CLIENT_SECRET']
CHANNEL_NAME = json.loads(os.environ['CHANNEL_NAME'])
BROADCASTER_ID = os.environ['BROADCASTER_ID']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']


