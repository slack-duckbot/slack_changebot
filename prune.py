# This script will archive all change channels
import os

from flask import Flask
import requests
import slack

app = Flask(__name__)
app.config.from_object(os.environ.get("FLASK_CONFIG", "app.config.DevelopmentConfig"))

client = slack.WebClient(token=app.config["SLACK_TOKEN"])
response = client.conversations_list()
channels = response["channels"]
for channel in channels:
    if (
        channel["name"].startswith(app.config["SLACK_CHANGE_CHANNEL_PREFIX"])
        and not channel["is_archived"]
    ):
        channel_id = channel["id"]
        requests.post(
            f"https://slack.com/api/channels.archive?token={app.config['SLACK_USER_TOKEN']}&channel={channel_id}"
        )
