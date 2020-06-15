import logging

from app import app
from app.helpers import slack as sl

client = sl.get_slack_client()


def release_change(form):
    channel_name = form["channel_name"]
    user_id = form["user_id"]
    channel_id = form["channel_id"]

    if not sl.is_change_channel(channel_name):
        logging.debug("Not a valid change channel")
        return False

    change_number = sl.get_change_number_from_channel_name(channel_name)

    client.chat_postMessage(
        channel=app.config["SLACK_ANNOUNCEMENTS_CHANNEL"],
        text=f"Change {change_number} is going live!",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":rocket: Change {change_number} is going live!",
                },
            },
            {
                "type": "section",
                "block_id": "channel_name",
                "text": {"type": "mrkdwn", "text": f"<#{channel_id}>",},
            },
            # {
            #     "type": "section",
            #     "block_id": "high_level_purpose",
            #     "text": {
            #         "type": "mrkdwn",
            #         "text": f"*High level purpose*\n{change_summary}",
            #     },
            # },
            {
                "type": "section",
                "block_id": "commander_info",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Mission Commander*\n<@{user_id}>"}
                ],
            },
            {"type": "divider"},
        ],
    )
