import os
import logging
import datetime
import pprint

from flask import jsonify, json
from flask import Flask
from flask import request, make_response

from slackeventsapi import SlackEventAdapter

from slack_helpers import get_next_change_number
import settings
from view_create_change import show_view_create_change
from view_edit_change import show_view_edit_change
from slack_helpers import get_slack_client, get_user_list, does_channel_exist
from feature_jira import create_jira_release
from feature_release_notes import post_release_notes, update_release_notes
from helpers_redis import (
    request_previously_responded,
    request_processed,
    redis_q,
)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("slack").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)

slack_events_adapter = SlackEventAdapter(settings.SLACK_SIGNING_SECRET, "/events", app)

CHANGES = {}


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return make_response("", 200)


@app.route("/commands", methods=["POST"])
def process_command():
    command_text = request.form["text"]
    logging.debug(f"Command received: {request.form['command']} {command_text}")

    user_id = request.form["user_id"]
    trigger_id = request.form["trigger_id"]

    if command_text == "new":
        show_view_create_change(trigger_id)
        return make_response("", 200)

    elif command_text == "next":
        next_change_number = get_next_change_number()
        return make_response(
            f"The next available change number is: *{next_change_number}*", 200
        )

    else:
        return make_response(
            f"*{command_text}* command is not supported currently.", 200
        )


@app.route("/interactive", methods=["POST"])
def process_interactive():

    message_payload = json.loads(request.form["payload"])
    user_id = message_payload["user"]["id"]
    user_name = message_payload["user"]["name"]
    trigger_id = message_payload["trigger_id"]

    if message_payload["type"] == "block_actions":
        change_summary_block = next(
            (
                block
                for block in message_payload["message"]["blocks"]
                if block["block_id"] == "txt_change_summary"
            ),
            None,
        )
        change_summary = change_summary_block["text"]["text"]
        release_notes_block = next(
            (
                block
                for block in message_payload["message"]["blocks"]
                if block["block_id"] == "txt_release_notes"
            ),
            None,
        )
        release_notes = release_notes_block["text"]["text"]
        channel_id = message_payload["channel"]["id"]
        message_ts = message_payload["message"]["ts"]
        metadata = {
            "channel_id": channel_id,
            "message_ts": message_ts,
            "change_summary": change_summary,
            "release_notes": release_notes,
        }

        show_view_edit_change(trigger_id, change_summary, release_notes, metadata)

        return make_response("", 200)

    if message_payload["type"] == "view_submission":
        callback_id = message_payload["view"]["callback_id"]

        if callback_id == "edit_change_modal":
            state_values = message_payload["view"]["state"]["values"]
            metadata = json.loads(message_payload["view"]["private_metadata"])

            change_summary = state_values["change_summary"]["txt_change_summary"][
                "value"
            ]
            release_notes = state_values["release_notes"]["txt_release_notes"]["value"]

            update_release_notes(metadata, user_id, change_summary, release_notes)

            redis_q.enqueue(
                get_slack_client().conversations_setPurpose,
                channel=metadata["channel_id"],
                purpose=change_summary,
            )

            redis_q.enqueue(
                get_slack_client().conversations_setTopic,
                channel=metadata["channel_id"],
                topic=change_summary,
            )

        if callback_id == "create_change_modal":

            state_values = message_payload["view"]["state"]["values"]
            change_number = state_values["change_no"]["txt_change_no"]["value"]
            change_summary = state_values["change_summary"]["txt_change_summary"][
                "value"
            ]
            try:
                release_notes = state_values["release_notes"]["txt_release_notes"][
                    "value"
                ]
            except KeyError as e:
                logging.debug("No release notes found in modal payload")
                release_notes = None

            new_channel_name = f"{settings.SLACK_CHANGE_CHANNEL_PREFIX}{change_number}"

            # Check to see if channel already exists, return an error if so
            if does_channel_exist(new_channel_name):

                return jsonify(
                    {
                        "response_action": "errors",
                        "errors": {
                            "change_no": "A channel already exists with this change number"
                        },
                    }
                )

            # Create the new channel and set purpose / topic
            new_channel = get_slack_client().conversations_create(name=new_channel_name)
            new_channel_id = new_channel["channel"]["id"]

            redis_q.enqueue(
                get_slack_client().conversations_setPurpose,
                channel=new_channel_id,
                purpose=change_summary,
            )

            redis_q.enqueue(
                get_slack_client().conversations_setTopic,
                channel=new_channel_id,
                topic=change_summary,
            )

            change_meta_field = [
                {"type": "mrkdwn", "text": f"*Channel*\n<#{new_channel_id}>"}
            ]

            jira_release_url = create_jira_release(
                change_number, user_name, change_summary
            )
            jira_field = None
            if jira_release_url is not False:
                change_meta_field.append(
                    {
                        "type": "mrkdwn",
                        "text": f"*Jira*\n<{jira_release_url}|C{change_number}>",
                    }
                )

            redis_q.enqueue(
                get_slack_client().chat_postMessage,
                channel=settings.SLACK_CHANGES_CHANNEL,
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
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Creator*\n<@{user_id}>"}
                        ],
                    },
                    {"type": "divider"},
                ],
            )

            if settings.ENABLE_RELEASE_NOTES:
                redis_q.enqueue(
                    post_release_notes,
                    new_channel_name,
                    new_channel_id,
                    change_summary,
                    release_notes,
                    user_id,
                )

            # Invite the original user into the channel, after release notes created so they don't get an alert
            redis_q.enqueue(
                get_slack_client().conversations_invite,
                channel=new_channel_id,
                users=[user_id],
            )

        return make_response("", 200)


@slack_events_adapter.on("channel_created")
def channel_created(event_data):
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
    user = get_slack_client().users_info(user=user_id)["user"]
    username = user["name"]
    log_entry["userId"] = user_id
    log_entry["username"] = username

    if request_previously_responded(event_id):
        logging.debug("Skipping duplicate request")
        log_entry["requestOutcome"] = "Duplicate-Responded"
        logging.debug(json.dumps(log_entry))
        return

    # Only notify a change when the channel was manually created by a human, to avoid picking up app creation events
    if (
        channel_name.startswith(settings.SLACK_CHANGE_CHANNEL_PREFIX) is True
        and user["is_bot"] is False
    ):

        # channel_id is used to pass within slack messages instead of name
        # so slack can handle private channels correctly.
        channel_info = get_slack_client().channels_info(channel=channel_id)
        channel_purpose = channel_info["channel"]["purpose"]["value"]

        get_slack_client().chat_postMessage(
            channel=settings.SLACK_CHANGES_CHANNEL,
            text=f"<@{user_id}> manually created <#{channel_id}>\n>*{channel_purpose}*",
        )

        # Add the completed event_id to the REQUESTS set
        request_processed(event_id)

        log_entry["requestOutcome"] = "Relevant-Completed"
        logging.debug(json.dumps(log_entry))

        return

    # Add the completed event_id to the REQUESTS set
    request_processed(event_id)

    log_entry["requestOutcome"] = "Irrelevant-Responded"
    logging.debug(json.dumps(log_entry))


@slack_events_adapter.on("channel_rename")
def channel_renamed(event_data):
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
        logging.debug(json.dumps(log_entry))
        return

    # Only notify a change when the channel was manually created by a human, to avoid picking up app creation events
    if channel_name.startswith(settings.SLACK_CHANGE_CHANNEL_PREFIX):

        # channel_id is used to pass within slack messages instead of name
        # so slack can handle private channels correctly.
        channel_info = get_slack_client().channels_info(channel=channel_id)
        channel_purpose = channel_info["channel"]["purpose"]["value"]

        get_slack_client().chat_postMessage(
            channel=settings.SLACK_CHANGES_CHANNEL,
            text=f"Channel renamed to *#{channel_name}* (<#{channel_id}>)\n>*{channel_purpose}*",
        )

        # Add the completed event_id to the REQUESTS set
        request_processed(event_id)

        log_entry["requestOutcome"] = "Relevant-Completed"
        logging.debug(json.dumps(log_entry))

        return

    # Add the completed event_id to the REQUESTS set
    request_processed(event_id)

    log_entry["requestOutcome"] = "Irrelevant-Responded"
    logging.debug(json.dumps(log_entry))


user_list = get_user_list()

# Start the server on port 5000
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
