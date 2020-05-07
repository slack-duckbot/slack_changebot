# This script will archive all change channels
import requests
import slack

import settings

client = slack.WebClient(token=settings.SLACK_TOKEN)
response = client.channels_list()
channels = response["channels"]
for channel in channels:
    if (
        channel["name"].startswith(settings.SLACK_CHANGE_CHANNEL_PREFIX)
        and not channel["is_archived"]
    ):
        channel_id = channel["id"]
        requests.post(
            f"https://slack.com/api/channels.archive?token={settings.SLACK_USER_TOKEN}&channel={channel_id}"
        )
