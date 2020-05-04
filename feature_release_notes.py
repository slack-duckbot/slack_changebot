import datetime

from slack_helpers import get_slack_client


def post_release_notes(
    state_values,
    new_channel_name,
    new_channel_id,
    change_number,
    change_summary,
    user_id,
):
    # If release notes are given, add those to the post. Otherwise still add it as an empty post.
    release_notes = " "
    if "value" in state_values["release_notes"]["txt_release_notes"]:
        release_notes = state_values["release_notes"]["txt_release_notes"]["value"]

    last_updated = datetime.datetime.today().strftime("%b %d, %Y at %I:%M %p")

    release_notes_post = get_slack_client().chat_postMessage(
        channel=new_channel_name,
        text=f"Change {change_number} initial release notes",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Description of change*"},
            },
            {
                "type": "section",
                "text": {"type": "plain_text", "text": change_summary, "emoji": True},
                "block_id": "txt_change_summary",
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Release notes - Change {change_number}*",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": release_notes},
                "block_id": "txt_release_notes",
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Edit"},
                    "value": "edit_release_notes",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Last updated: { last_updated } by <@{user_id}>",
                    }
                ],
            },
        ],
    )

    get_slack_client().pins_add(
        channel=new_channel_id, timestamp=release_notes_post["ts"]
    )
