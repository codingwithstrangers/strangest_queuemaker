import os
import json
from dotenv import load_dotenv
load_dotenv()
USER_TOKEN = 'mqsmmszekcnq8rp9vuk0gpt5f2y0id'
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET= os.environ['CLIENT_SECRET']
CHANNEL_NAME = json.loads(os.environ['CHANNEL_NAME'])
BROADCASTER_ID = os.environ['BROADCASTER_ID']
REFRESH_TOKEN = '9861ie8elf2wmz89paijqm19fx7c5di0nuxiw7axgxzty7vq5x'
