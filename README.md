# changebot v0.1

## Windows installation

- Install python via store (from python.org was not working from either git bash (permission denied) nor powershell (opened store))
- pip install -r requirements.txt
- Install ngrok so you can tunnel the bot into slack
- Make a .env file with the variables used in settings.py
- SLACK_TOKEN is Bot User OAuth Access Token
- Works with following scopes (some may not be needed): users:read, commands, chat:write, channels:read, channels:manage, channels:join, channels:history
- Interactivity should be enabled with redirect going to /interactive
- Make a slash command (arbitary name) with request URL going to /commands
- Add /events URL to events subscriptions and enable

## Environment Variables
You will need a .env file with the following
```
SLACK_SIGNING_SECRET=
SLACK_TOKEN=


JIRA_USERNAME=
JIRA_PASSWORD=
JIRA_SERVER=
JIRA_PROJECT_KEY=TEST111
ENABLE_JIRA_INTEGRATION=False
```

ENABLE_JIRA_INTEGRATION is used as a flag to enable/disable Jira integration.