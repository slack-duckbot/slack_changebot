import logging

from app import app
from app.helpers import slack as sl

client = sl.get_slack_client()


def change_going_live(form):
    channel_name = form["channel_name"]
    user_id = form["user_id"]
    channel_id = form["channel_id"]

    if not sl.is_change_channel(channel_name):
        logging.debug("Not a valid change channel")
        return False

    purpose = sl.get_channel_purpose(channel_id)

    client.chat_postMessage(
        channel=app.config["SLACK_ANNOUNCEMENTS_CHANNEL"],
        text=f"<#{channel_id}> is going live!",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":rocket: <#{channel_id}> is going live!",
                },
            },
            {
                "type": "section",
                "block_id": "high_level_purpose",
                "text": {"type": "mrkdwn", "text": f"*Change summary:* {purpose}",},
            },
            {
                "type": "section",
                "block_id": "commander_info",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Mission Commander:* <@{user_id}>"}
                ],
            },
            {"type": "divider"},
        ],
    )

    client.chat_postMessage(
        channel=channel_id,
        text=f"This change is going live!",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":rocket: This change is going live!",
                },
            },
            {
                "type": "section",
                "block_id": "commander_info",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Mission Commander:* <@{user_id}>"}
                ],
            },
            {"type": "divider"},
        ],
    )
