import json
import logging

import slack

from app.helpers.redis import redis_q
from app.helpers.slack import get_slack_client, get_next_change_number


client = get_slack_client()


def show_view_create_change_start(trigger_id, form):
    logging.info("Showing View: Create Change Start")

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
        "submit": {"type": "plain_text", "text": "Quack"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Preening feathers...*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Duckbot has to distract you with this view whilst it does some quick prep to help comply "
                    "with Slack's timeout rules..._",
                },
            },
        ],
    }
    try:
        client.views_open(trigger_id=trigger_id, view=modal)
    except slack.errors.SlackApiError:
        logging.exception("Got SlackAPI error")

    # We get the latest conversations list here to cache it for use by the Create Change view (ttl is 30 seconds)
    # With large conversations lists, I've found it takes too long to do immediately before creating the view, which
    # causes the interaction trigger to expire.
    redis_q.enqueue(get_next_change_number)
