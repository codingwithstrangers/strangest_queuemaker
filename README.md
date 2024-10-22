<div id="header" align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjAyMXphYmdkeWhsZjdzNWIyMjg0MGt5N3Rxd3dvZnFjZ2NuZXExMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/jvOHlU7qhcnsEGuTQZ/giphy.gif" width="150"/>
</div>

<p align="center">
  <img src="https://i.imgur.com/R6Wc7RQ.jpg" alt="Image Description" width="400"/>
</p>

### The Strangest Queue

This project is a Twitch song request bot that processes bit donations, adds songs to a queue, and tracks song playback time using a countdown timer. The bot also handles failed queues, gives priority to high-donation songs, and automatically scrolls through user-submitted songs in a web interface. This bot can be used to run a Subathon or queue list. Every sub and song added increases time on the timer.

<pre align="center">
----------------------------------------------------
</pre>

<div align="center"><h3>Subathon:</h3> A live streaming event where a content creator or gamer continuously streams for an extended period, typically with the goal of reaching a certain number of subscribers or followers. The term is short for "subscription marathon."</div>

<div align="center"><h3>Queue:</h3> A list of data items, commands, etc., stored to be retrievable in a definite order, usually in the order of insertion.</div>

<pre align="center">
----------------------------------------------------
</pre>

### What is This
It's a bot that will count down from a certain number and every song added or sub will increase the time. The bot listens for subs and bits. I couldn't find a bot that does both in one. You will need a Twitch account and a developer account, both easy to set up and use. The TwitchIO documentation is difficult to digest, but I did the hard part—just follow my lead. The access_token is the token you get from the [twitchiogenerator](https://twitchtokengenerator.com). They call it a token in the documents. You should also make a refresh token page to handle this for you in the future. Potential updates could include running a routine to do this automatically every 3 hours for you.

This bot can be run locally or on a server, mixing JS and Python to make a stream overlay (I know, I know—why didn’t I use Flask?).

### Why Did I Do This

I wanted a way to securely receive donations from Twitch and give something in return. Additionally, I wanted to explore how a Python backend could run a JS frontend. It worked seamlessly.

### How Users Can Use This

**For Users:**
- Hire a programmer.
- Tell them to read this.
- Just kidding! It’s not that bad. I think this would be a great project to test your skills.

**For Programmers:**
Here’s a summary of how it works. Be advised that the Godot aspect is used for display purposes. You can send the event to any platform for display, but I prefer Godot.

### Installation

1. **Flow of Event Handling and Queue Management**
   - This bot is broken into 3 parts, all based on JSON.
   - `main.py` generates a JSON and TXT file.
   - `queue.json` reads that JSON to build the table below (see image above).
   - The `all_songs.json` is just a running list I made, but you can create your own if needed.
   - If your JSON isn’t updating (i.e., adding rows), it’s a Python issue; if it isn’t updating colors or checkboxes, it’s a JS issue.
   - Focus on understanding the logic for both Python and JavaScript, and you’ll be fine.

2. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/twitchio-song-request-bot.git
    cd twitchio-song-request-bot
    ```

3. **Install Python Dependencies**:
    Make sure you have Python 3.10.6 installed. Then install the required Python libraries:
    ```bash
    pip install twitchio asyncio json re datetime
    ```

4. **Install JavaScript Dependencies**:
    The project does not require additional JavaScript libraries. It relies on the native Fetch API and localStorage.

5. **Configure Environment Variables**:
    Create a `configuration.py` file to store the following variables:
    ```python
    import os
    import json
    from dotenv import load_dotenv
    load_dotenv()
    
    USER_TOKEN = os.environ['USER_TOKEN']
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    CHANNEL_NAME = json.loads(os.environ['CHANNEL_NAME'])
    BROADCASTER_ID = os.environ['BROADCASTER_ID']
    REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
    ```

## APIs

### Twitch API (TwitchIO):
- **PubSub API**: This is used to subscribe to events such as Bits donations and channel points redemptions.
- **OAuth API**: Refresh tokens are handled by the OAuth flow to keep the bot connected and authorized to interact with the channel.

## Features

1. **Song Queue**:
   - Songs are added to a queue based on Twitch chat messages containing a CWS number and bits. Users can prioritize songs by donating bits.
   - Regular and DLC songs are distinguished, and different bit thresholds apply for each.

2. **Song Timer**:
   - A countdown timer tracks the total time, and songs added increase the time.
   - Bit donations or subscriptions can add time to the queue (1 hour for subscriptions, and additional time based on song length for donations).
   - The timer is automatically updated as songs are added or removed.

3. **User Profiles**:
   - User profiles are stored in `user_profiles.json`, tracking requested songs, donation amounts, and whether the request was prioritized.
   - Profiles are sorted based on donation amount and priority status.

4. **Error Handling**:
   - If a user attempts to request a song without enough bits, a message is sent in chat, and the failed request is logged to `failed_queue.txt`.

5. **Auto-Scrolling Queue**:
   - The song queue automatically scrolls every 3 seconds when more than 7 songs are in the queue.
   - Scrolling pauses when the user hovers over the queue.

## Usage

1. **Run the Python Script**:
    To start the bot, simply run the `main.py` file:
    ```bash
    python main.py
    ```

2. **Interact with Twitch Chat**:
    - Users can request songs in chat using a CWS number (e.g., `CWS_83`).
    - They can prioritize their request by donating bits over the set limit.

3. **Subscribe to Events**:
    - The bot listens for PubSub events such as Bit donations and channel points redemptions.
    - On a new subscription, 1 hour is added to the song queue timer.

## JavaScript Functionality

- The JavaScript code dynamically fetches user profiles from `user_profiles.json` and populates the song queue on a web page.
- **Checkbox State**:
   - Each song in the queue has a checkbox that, when checked, greys out the song and adds a strikethrough to mark it as done.
   - Checkbox states are stored in `localStorage` to persist across browser sessions.
   
- **Auto-Scrolling**:
   - When the queue exceeds 7 songs, it automatically scrolls every 3 seconds.
   - Scrolling pauses when the user hovers over the song list, resuming once the cursor leaves.

### Need Help?

[![Twitter Follow](https://img.shields.io/badge/Twitter-Follow%20%40strangestcoder-1DA1F2?style=for-the-badge&logo=twitter)](https://x.com/strangestcoder)

[![Twitch Status](https://img.shields.io/badge/Twitch-Live%20Codingwithstrangers-9146FF?style=for-the-badge&logo=twitch)](https://www.twitch.tv/codingwithstrangers)

### Who is Doing This

Coding with Strangers, aka Heero

### Bugs or Updates

I really enjoyed working on this project; it pushed me to learn a lot about streaming events, cross-platform connections, and how to structure my code better. If I return to this code, I might rewrite it fully in Godot and link it to a server so it can run in the cloud. However, if you want to find new bugs and fix old ones, feel free to dive in!

- [ ] The message for subs doesn’t work
- [ ] I wanted to use Spotify’s API to add the actual length of a song to the timer but ran out of time
- [ ] Maybe make the font bigger?
