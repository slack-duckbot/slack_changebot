
from slack_helpers import get_slack_client
from settings import ENABLE_RELEASE_NOTES

def show_view_create_change(trigger_id):
    modal = {
        "type": "modal",
        "callback_id": "create_change_modal",
        "title": {
            "type": "plain_text",
            "text": "Create change channel",
            "emoji": True,
        },
        "submit": { "type": "plain_text", "text": "Create" },
        "close": { "type": "plain_text", "text": "Cancel" },
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_change_no",
                    "multiline": False,
                },
                "block_id": "change_no",
                "label": {
                    "type": "plain_text",
                    "text": "Change Number",
                    "emoji": False,
                },
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "txt_change_summary",
                    "multiline": False,
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

    if ENABLE_RELEASE_NOTES:
        modal["blocks"].append({
            "type": "input",
            "block_id": "release_notes",
            "optional": True,
            "label": {
                "type": "plain_text",
                "text": "Release notes"
            },
            "element": {
                "type": "plain_text_input",
                "action_id": "txt_release_notes",
                "multiline": True,
            }
        })

        

    view_open = get_slack_client().views_open(trigger_id=trigger_id, view=modal)

    print(view_open["view"]["id"])