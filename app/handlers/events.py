import datetime
import json
import logging

from slackeventsapi import SlackEventAdapter

from app import app
from app.helpers.slack import get_slack_client
from app.helpers.redis import request_previously_responded, request_processed

slack_events_adapter = SlackEventAdapter(
    app.config["SLACK_SIGNING_SECRET"], "/events", app
)

client = get_slack_client()


@slack_events_adapter.on("channel_created")
def event_channel_created(event_data):
    log_entry = {}

    event_id = event_data["event_id"]

    # Get the name of the new channel, and the ID of the creator
    channel_id = event_data["event"]["channel"]["id"]
    channel_name = event_data["event"]["channel"]["name"]

    log_entry["timestamp"] = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    log_entry["event"] = "channel_created"
    log_entry["eventId"] = event_id
    log_entry["channelId"] = channel_id
    log_entry["channelName"] = channel_name

    # Get the creator's info via the Web API
    user_id = event_data["event"]["channel"]["creator"]
    user = client.users_info(user=user_id)["user"]
    username = user["name"]
    log_entry["userId"] = user_id
    log_entry["username"] = username

    if request_previously_responded(event_id):
        logging.debug("Skipping duplicate request")
        log_entry["requestOutcome"] = "Duplicate-Responded"
        logging.debug("Channel Created Event: Duplicate")

    # Only notify a change when the channel was manually created by a human, to avoid picking up app creation events
    if (
        channel_name.startswith(app.config["SLACK_CHANGE_CHANNEL_PREFIX"]) is True
        and user["is_bot"] is False
    ):

        # channel_id is used to pass within slack messages instead of name
        # so slack can handle private channels correctly.
        channel_info = client.conversations_info(channel=channel_id)
        channel_purpose = channel_info["channel"]["purpose"]["value"]

        client.chat_postMessage(
            channel=app.config["SLACK_CHANGES_CHANNEL"],
            text=f"<@{user_id}> manually created <#{channel_id}>\n>*{channel_purpose}*",
        )

        log_entry["requestOutcome"] = "Relevant-Completed"
        logging.debug("Channel Created Event: Message Posted")

    else:

        log_entry["requestOutcome"] = "Irrelevant-Responded"
        logging.debug("Channel Created Event: Ignored")

    # Add the completed event_id to the REQUESTS set
    request_processed(event_id)

    logging.debug(log_entry)


@slack_events_adapter.on("channel_rename")
def event_channel_renamed(event_data):
    log_entry = {}

    event_id = event_data["event_id"]

    # Get the name of the new channel, and the ID of the creator
    channel_id = event_data["event"]["channel"]["id"]
    channel_name = event_data["event"]["channel"]["name"]

    log_entry["timestamp"] = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    log_entry["event"] = "channel_renamed"
    log_entry["eventId"] = event_id
    log_entry["channelId"] = channel_id
    log_entry["channelName"] = channel_name

    if request_previously_responded(event_id):
        logging.debug("Skipping duplicate request")
        log_entry["requestOutcome"] = "Duplicate-Responded"
        logging.debug(f"Channel Rename Event: Duplicate")
        return

    # Only notify a change when the channel was manually created by a human, to avoid picking up app creation events
    if channel_name.startswith(app.config["SLACK_CHANGE_CHANNEL_PREFIX"]):

        # channel_id is used to pass within slack messages instead of name
        # so slack can handle private conversations correctly.
        channel_info = client.conversations_info(channel=channel_id)
        channel_purpose = channel_info["channel"]["purpose"]["value"]

        client.chat_postMessage(
            channel=app.config["SLACK_CHANGES_CHANNEL"],
            text=f"Channel renamed to *#{channel_name}* (<#{channel_id}>)\n>*{channel_purpose}*",
        )

        # Add the completed event_id to the REQUESTS set
        request_processed(event_id)

        log_entry["requestOutcome"] = "Relevant-Completed"
        logging.debug(f"Channel Rename Event - Message Posted")

    else:

        log_entry["requestOutcome"] = "Irrelevant-Responded"
        logging.debug("Channel Created Event: Ignored")

    # Add the completed event_id to the REQUESTS set
    request_processed(event_id)

    logging.debug(log_entry)
