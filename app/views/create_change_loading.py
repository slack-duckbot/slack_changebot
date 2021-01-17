import json

from app.helpers.slack import get_slack_client
from app import app

client = get_slack_client()


def show_view_create_change_loading(trigger_id, form):
    channel_id = form["channel_id"]

    modal = {
        "private_metadata": json.dumps({"channel_id": channel_id}),
        "type": "modal",
        "callback_id": "create_change_loading_modal",
        "title": {
            "type": "plain_text",
            "text": "Create change channel",
            "emoji": True,
        },
        "submit": {"type": "plain_text", "text": "Go"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Duckbot will help you create a new channel now...",
                },
            },
        ],
    }

    client.views_open(trigger_id=trigger_id, view=modal)
