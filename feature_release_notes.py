import datetime

from slack_helpers import get_slack_client


def post_release_notes(
    new_channel_name,
    new_channel_id,
    change_number,
    change_summary,
    release_notes,
    user_id,
):
    # If release notes are given, add those to the post. Otherwise still add it as an empty post.
    if not release_notes:
        release_notes = " "

    last_updated = datetime.datetime.today().strftime("%b %d, %Y at %I:%M %p")

    release_notes_post = get_slack_client().chat_postMessage(
        channel=new_channel_name,
        text=f"Channel <#{new_channel_id}> initial release notes",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Change Summary*"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Edit"},
                    "value": "btn_edit_rns",
                },
            },
            {
                "type": "section",
                "text": {"type": "plain_text", "text": change_summary, "emoji": True},
                "block_id": "txt_change_summary",
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Release Notes*"},},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": release_notes,},
                "block_id": "txt_release_notes",
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


def update_release_notes(metadata, user_id, change_summary, release_notes):

    last_updated = datetime.datetime.today().strftime("%b %d, %Y at %I:%M %p")

    release_notes_post = get_slack_client().chat_update(
        channel=metadata["channel_id"],
        ts=metadata["message_ts"],
        text=f"Channel <#{metadata['channel_id']}> initial release notes",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Change Summary*"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Edit"},
                    "value": "btn_edit_rns",
                },
            },
            {
                "type": "section",
                "text": {"type": "plain_text", "text": change_summary, "emoji": True},
                "block_id": "txt_change_summary",
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Release Notes*"},},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": release_notes,},
                "block_id": "txt_release_notes",
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Last updated: {last_updated} by <@{user_id}>",
                    }
                ],
            },
        ],
    )
