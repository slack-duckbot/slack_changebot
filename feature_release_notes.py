import datetime

from helpers.helpers_slack import get_slack_client
import settings


def post_release_notes(
    change_number,
    new_channel_name,
    new_channel_id,
    change_summary,
    release_notes,
    user_id,
    trello_release_url,
):
    # If release notes are given, add those to the post. Otherwise still add it as an empty post.
    if not release_notes:
        release_notes = " "

    last_updated = datetime.datetime.today().strftime("%b %d, %Y at %I:%M %p")

    change_meta_field = [{"type": "mrkdwn", "text": f"*Change No*\n{change_number}"}]

    if trello_release_url:
        change_meta_field.append(
            {
                "type": "mrkdwn",
                "text": f"*Trello*\n<{trello_release_url}|{settings.TRELLO_PREFIX}{change_number}>",
            }
        )

    release_notes_post = get_slack_client().chat_postMessage(
        channel=new_channel_name,
        text=f"Channel <#{new_channel_id}> initial release notes",
        blocks=[
            {
                "type": "section",
                "block_id": "change_meta",
                "fields": change_meta_field,
            },
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
