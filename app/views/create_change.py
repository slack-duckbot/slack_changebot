import json

from app.helpers.slack import get_slack_client, get_next_change_number
from app import app

client = get_slack_client()


def show_view_create_change(trigger_id, form):
    next_change_number = get_next_change_number()
    channel_id = form["channel_id"]

    modal = {
        "private_metadata": json.dumps({"channel_id": channel_id}),
        "type": "modal",
        "callback_id": "create_change_modal",
        "title": {
            "type": "plain_text",
            "text": "Create change channel",
            "emoji": True,
        },
        "submit": {"type": "plain_text", "text": "Create"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_change_no",
                    "multiline": False,
                    "initial_value": f"{next_change_number}",
                },
                "block_id": "change_no",
                "label": {
                    "type": "plain_text",
                    "text": "Change Number",
                    "emoji": False,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":exclamation: Remember to check the Trello Release Board :exclamation:\n:eyes: <https://trello.com/b/cj665kSN/111-ol-release-board> :eyes:",
                },
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_change_summary",
                    "multiline": False,
                    "placeholder": {"type": "plain_text", "text": " "},
                },
                "block_id": "change_summary",
                "label": {
                    "type": "plain_text",
                    "text": "Summary of change",
                    "emoji": False,
                },
            },
        ],
    }

    if app.config["ENABLE_RELEASE_NOTES"]:
        modal["blocks"].append(
            {
                "type": "input",
                "block_id": "release_notes",
                "optional": True,
                "label": {"type": "plain_text", "text": "Release notes"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_release_notes",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": " "},
                },
            }
        )

    client.views_open(trigger_id=trigger_id, view=modal)
