# changebot

## Windows installation

- Install python via store (from python.org was not working from either git bash (permission denied) nor powershell (opened store))
- pip install -r requirements.txt
- Install ngrok so you can tunnel the bot into slack
- Make a .env file with the variables used in settings.py
- SLACK_TOKEN is Bot User OAuth Access Token
- Works with following scopes (some may not be needed): users:read, commands, chat:write, channels:read, channels:manage, channels:join, channels:history
- Interactivity should be enabled with redirect going to /interactive
- Make a slash command (arbitary name) with request URL going to /commands