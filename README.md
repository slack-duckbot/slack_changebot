# changebot v0.3

## Windows installation

- Install python via store (from python.org was not working from either git bash (permission denied) nor powershell (opened store))
- `pip install -r requirements.txt`
- Install ngrok so you can tunnel the bot into slack
- Make a .env file with the variables used in `settings.py` (you can use `template.env` and renamve to `.env`)
- SLACK_TOKEN is Bot User OAuth Access Token
- Works with following scopes (some may not be needed): users:read, commands, chat:write, channels:read, channels:manage, channels:join, channels:history, files:write, pins:write
- Interactivity should be enabled with redirect going to /interactive
- Make a slash command (arbitary name) with request URL going to /commands
- Add /events URL to events subscriptions and enable

## Environment Variables

You will need a .env file with the following (you can use template.env to get you started)

```
FLASK_APP=bot
FLASK_ENV=development
ENVIRONMENT_NAME=dev

SLACK_SIGNING_SECRET=
SLACK_TOKEN=
SLACK_CHANGES_CHANNEL=changes
SLACK_CHANGE_CHANNEL_PREFIX=change-
SLACK_ANNOUNCEMENTS_CHANNEL=announcements
SLACK_USER_TOKEN=

ENABLE_RELEASE_NOTES=True

JIRA_USERNAME=
JIRA_PASSWORD=
JIRA_SERVER=
JIRA_PROJECT_KEY=
ENABLE_JIRA_INTEGRATION=False

TRELLO_API_KEY=
TRELLO_TOKEN=
TRELLO_LIST_ID=
TRELLO_LIST_IDS=["", ""]        -- Must be provided as a list with 1 or more elements
TRELLO_PREFIX=
ENABLE_TRELLO_INTEGRATION=True
```

ENABLE_RELEASE_NOTES enables the posting of release notes when new change channels are created.
ENABLE_JIRA_INTEGRATION enables creation of Jira releases for new changes.

## Trello Integration

`ENABLE_TRELLO_INTEGRATION` enables creation of Trello cards for new changes.

You can get a Trello API Key at https://trello.com/app-key
You will need to get a Token too, which is linked from that page.

The Trello list ID can be found by adding `.json` onto your Trello board URL.


## Background Workers

This app makes use of the *rq* library to put async jobs onto a background worker queue.

The worker queue is stored in Redis, so you will need a Redis instance available to run the app.

The Redis connection details are set in an environment variable e.g.

`export REDIS_URL=redis://localhost:6379`

### Running a background worker
To run a background worker, use the command `rq worker` (will default to `redis://localhost:6379` connection)

To specify a different connection URL, use `rq worker --url redis://user:secrets@a.different.host:1234/0`

### Running a local instance of Redis using Docker

If you have Docker installed, you can spin up a simple Redis container 

`docker run -d -p 6379:6379 redis`
