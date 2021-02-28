import json
import logging

import requests

from app.helpers.slack import get_slack_client

client = get_slack_client()


def rename_channel(form):
    trigger_id = form["trigger_id"]
    channel_id = form["channel_id"]
    channel_name = form["channel_name"]
    bot_user_id = client.auth_test()["user_id"]
    conversation_info = client.conversations_info(channel=form["channel_id"])

    # The bot can only rename the channel if it created it in the first place
    if conversation_info["channel"]["creator"] != bot_user_id:
        message = {"text": "I didn't create this channel so I can't rename it :("}
        requests.post(url=form["response_url"], json=message)
        logging.debug("Conversation Rename Command: Conversation not owned by bot")
        return

    metadata = {"channel_id": channel_id}

    modal = {
        "type": "modal",
        "callback_id": "rename_conversation_modal",
        "title": {
            "type": "plain_text",
            "text": "Rename conversation",
            "emoji": True,
        },
        "submit": {"type": "plain_text", "text": "Rename"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "block_id": "new_name",
                "type": "input",
                "label": {
                    "type": "plain_text",
                    "text": "New name",
                    "emoji": False,
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_new_name",
                    "multiline": False,
                },
            },
        ],
        "private_metadata": json.dumps(metadata),
    }

    client.views_open(trigger_id=trigger_id, view=modal)
