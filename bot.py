import os
import logging
import datetime
from flask import jsonify, json
from flask import Flask
from flask import request, make_response
from slack import WebClient
from slackeventsapi import SlackEventAdapter

import settings
from feature_jira import create_jira_release


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("slack").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

app = Flask(__name__)


def get_slack_client():
    return WebClient(token=settings.SLACK_TOKEN)


client = WebClient(token=settings.SLACK_TOKEN)
slack_events_adapter = SlackEventAdapter(settings.SLACK_SIGNING_SECRET, "/events", app)

CHANGES = {}

# Create a set which will provide simple idempotency support for event callbacks
REQUESTS = set()


def get_user_list():
    response = client.users_list()

    members = response["members"]
    user_ids = []

    for member in members:
        user = {"user_id": member["id"], "name": member["name"]}
        user_ids.append(user)

    return user_ids


def does_channel_exist(channel_name):
    response = client.channels_list()

    channels = response["channels"]

    results = [channel for channel in channels if channel["name"] == channel_name]
    print(results)
    if len(results) > 0:
        return True
    else:
        return False


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return make_response("", 200)


@app.route("/commands", methods=["POST"])
def process_command():
    logging.debug(request.form["command"])
    logging.debug(request.form["text"])
    logging.debug(request.form)

    user_id = request.form["user_id"]
    trigger_id = request.form["trigger_id"]

    # Add the message_ts to the user's order info
    view_open = client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "create_change_modal",
            "title": {
                "type": "plain_text",
                "text": "Create change channel",
                "emoji": True,
            },
            "submit": {"type": "plain_text", "text": "Create", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
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
                },
            ],
        },
    )

    print(view_open["view"]["id"])

    return make_response("", 200)


@app.route("/interactive", methods=["POST"])
def process_interactive():

    logging.debug(request.form)

    message_payload = json.loads(request.form["payload"])
    user_id = message_payload["user"]["id"]
    user_name = message_payload["user"]["name"]

    if message_payload["type"] == "view_submission":

        state_values = message_payload["view"]["state"]["values"]

        change_number = state_values["change_no"]["txt_change_no"]["value"]
        change_summary = state_values["change_summary"]["txt_change_summary"]["value"]

        new_channel_name = f"{settings.SLACK_CHANGE_CHANNEL_PREFIX}{change_number}"

        # Check to see if channel already exists, return an error if so
        if does_channel_exist(new_channel_name):

            return jsonify(
                {"response_action": "errors",
                 "errors": {"change_no": "A channel already exists with this change number"}
                }
            )

        # Create the new channel and set purpose / topic
        new_channel = client.conversations_create(name=new_channel_name)
        new_channel_id = new_channel["channel"]["id"]

        get_slack_client().conversations_setPurpose(
            channel=new_channel_id, purpose=change_summary
        )

        get_slack_client().conversations_setTopic(channel=new_channel_id, topic=change_summary)

        # Invite the original user into the channel
        get_slack_client().conversations_invite(channel=new_channel_id, users=[user_id])
        jira_release_url = create_jira_release(change_number, user_name, change_summary)
        jira_text = ""
        if jira_release_url is not False:
            jira_text = f"\n*Jira release:* <{jira_release_url}>"

        get_slack_client().chat_postMessage(
            channel=settings.SLACK_CHANGES_CHANNEL,
            text=f"<@{user_id}> created <#{new_channel_id}>\n>*{change_summary}*{jira_text}",
        )

        return make_response("", 200)


@slack_events_adapter.on("channel_created")
def channel_created(event_data):
    log_entry = {}

    event_id = event_data["event_id"]

    # Get the name of the new channel, and the ID of the creator
    channel_id = event_data["event"]["channel"]["id"]
    channel_name = event_data["event"]["channel"]["name"]

    log_entry["timestamp"] = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
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

    if event_id in REQUESTS:
        logging.debug("Skipping duplicate request")
        log_entry["requestOutcome"] = "Duplicate-Responded"
        logging.debug(json.dumps(log_entry))
        return

    # Only notify a change when the channel was manually created by a human, to avoid picking up app creation events
    if channel_name.startswith(settings.SLACK_CHANGE_CHANNEL_PREFIX) is True and user["is_bot"] is False:

        # channel_id is used to pass within slack messages instead of name
        # so slack can handle private channels correctly.
        channel_info = client.channels_info(channel=channel_id)
        channel_purpose = channel_info['channel']['purpose']['value']

        client.chat_postMessage(
            channel=settings.SLACK_CHANGES_CHANNEL,
            text=f"<@{user_id}> manually created <#{channel_id}>\n>*{channel_purpose}*",
        )

        # Add the completed event_id to the REQUESTS set
        REQUESTS.add(event_id)

        log_entry["requestOutcome"] = "Relevant-Completed"
        logging.debug(json.dumps(log_entry))

        return

    # Add the completed event_id to the REQUESTS set
    REQUESTS.add(event_id)

    log_entry["requestOutcome"] = "Irrelevant-Responded"
    logging.debug(json.dumps(log_entry))


@slack_events_adapter.on("channel_rename")
def channel_renamed(event_data):
    log_entry = {}

    event_id = event_data["event_id"]

    # Get the name of the new channel, and the ID of the creator
    channel_id = event_data["event"]["channel"]["id"]
    channel_name = event_data["event"]["channel"]["name"]

    log_entry["timestamp"] = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    log_entry["event"] = "channel_renamed"
    log_entry["eventId"] = event_id
    log_entry["channelId"] = channel_id
    log_entry["channelName"] = channel_name

    if event_id in REQUESTS:
        logging.debug("Skipping duplicate request")
        log_entry["requestOutcome"] = "Duplicate-Responded"
        logging.debug(json.dumps(log_entry))
        return

    # Only notify a change when the channel was manually created by a human, to avoid picking up app creation events
    if channel_name.startswith(settings.SLACK_CHANGE_CHANNEL_PREFIX):

        # channel_id is used to pass within slack messages instead of name
        # so slack can handle private channels correctly.
        channel_info = get_slack_client().channels_info(channel=channel_id)
        channel_purpose = channel_info['channel']['purpose']['value']

        get_slack_client().chat_postMessage(
            channel=settings.SLACK_CHANGES_CHANNEL,
            text=f"Channel renamed to <#{channel_id}>\n>*{channel_purpose}*",
        )

        # Add the completed event_id to the REQUESTS set
        REQUESTS.add(event_id)

        log_entry["requestOutcome"] = "Relevant-Completed"
        logging.debug(json.dumps(log_entry))

        return

    # Add the completed event_id to the REQUESTS set
    REQUESTS.add(event_id)

    log_entry["requestOutcome"] = "Irrelevant-Responded"
    logging.debug(json.dumps(log_entry))


user_list = get_user_list()

# Start the server on port 5000
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
