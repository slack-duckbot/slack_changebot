import json

from app.helpers.slack import get_slack_client
from app import app

client = get_slack_client()


def show_view_edit_change(trigger_id, change_summary, release_notes, metadata):
    modal = {
        "type": "modal",
        "callback_id": "edit_change_modal",
        "private_metadata": json.dumps(metadata),
        "title": {"type": "plain_text", "text": "Edit change channel", "emoji": True,},
        "submit": {"type": "plain_text", "text": "Edit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_change_summary",
                    "multiline": False,
                    "initial_value": change_summary,
                },
                "block_id": "change_summary",
                "label": {
                    "type": "plain_text",
                    "text": "Summary of change",
                    "emoji": False,
                },
            }
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
                    "initial_value": release_notes,
                },
            }
        )

    view_open = client.views_open(trigger_id=trigger_id, view=modal)

    return view_open
