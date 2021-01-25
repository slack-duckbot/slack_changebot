import logging

from app import app
from app.helpers import slack as sl
from app.features import trello, jira, release_notes as rn

client = sl.get_slack_client()


def create_change(message_payload):

    user_id = message_payload["user"]["id"]
    user_name = message_payload["user"]["name"]

    state_values = message_payload["view"]["state"]["values"]
    change_number = state_values["change_no"]["txt_change_no"]["value"]

    new_channel_name = f"{app.config['SLACK_CHANGE_CHANNEL_PREFIX']}{change_number}"
    change_summary = state_values["change_summary"]["txt_change_summary"]["value"]

    try:
        release_notes = state_values["release_notes"]["txt_release_notes"]["value"]

    except KeyError:
        logging.debug("No release notes found in modal payload")
        release_notes = None

    # Create the new channel and set purpose / topic
    new_channel = client.conversations_create(name=new_channel_name)
    new_channel_id = new_channel["channel"]["id"]

    client.conversations_setPurpose(channel=new_channel_id, purpose=change_summary)

    client.conversations_setTopic(channel=new_channel_id, topic=change_summary)

    change_meta_field = [{"type": "mrkdwn", "text": f"*Channel*\n<#{new_channel_id}>"}]

    jira_release_url = jira.create_jira_release(change_number, user_name, change_summary)

    if jira_release_url is not False:
        change_meta_field.append(
            {
                "type": "mrkdwn",
                "text": f"*Jira*\n<{jira_release_url}|{app.config['JIRA_PREFIX']}{change_number}>",
            }
        )

    trello_release_url = trello.create_trello_cards(
        change_number, user_name, change_summary, release_notes
    )

    if trello_release_url:
        change_meta_field.append(
            {
                "type": "mrkdwn",
                "text": f"*Trello*\n<{trello_release_url}|{app.config['TRELLO_PREFIX']}{change_number}>",
            }
        )

    client.chat_postMessage(
        channel=app.config["SLACK_CHANGES_CHANNEL"],
        text=f"Change {change_number} created by <@{user_id}>",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": ":bulb: New change created"},
            },
            {
                "type": "section",
                "block_id": "high_level_purpose",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*High level purpose*\n{change_summary}",
                },
            },
            {
                "type": "section",
                "block_id": "change_meta",
                "fields": change_meta_field,
            },
            {
                "type": "section",
                "block_id": "creation_info",
                "fields": [{"type": "mrkdwn", "text": f"*Creator*\n<@{user_id}>"}],
            },
            {"type": "divider"},
        ],
    )

    if app.config["ENABLE_RELEASE_NOTES"]:
        rn.post_release_notes(
            change_number,
            new_channel_name,
            new_channel_id,
            change_summary,
            release_notes,
            user_id,
            trello_release_url,
        )

    # Invite the original user plus any selected users into the channel
    # We invite after release notes are created so they don't get a message alert straight away
    try:
        selected_users = state_values["users_select"]["selected_users"][
            "selected_users"
        ]
    except KeyError:
        selected_users = []

    selected_users.append(user_id)

    client.conversations_invite(channel=new_channel_id, users=selected_users)
