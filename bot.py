import os
import sys
import logging
import requests
from pprint import pprint, pformat
from flask import jsonify, json
from flask import Flask
from flask import request, Response, make_response
import slack
from slackeventsapi import SlackEventAdapter

import settings

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("slack").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

app = Flask(__name__)

client = slack.WebClient(token=settings.SLACK_TOKEN)
slack_events_adapter = SlackEventAdapter(settings.SLACK_SIGNING_SECRET, "/events", app)

CHANGES = {}


def get_user_list():
    response = client.users_list()

    members = response["members"]
    user_ids = []

    for member in members:
        user = {"user_id": member["id"], "name": member["name"]}
        user_ids.append(user)

    return user_ids


def create_channel(channel_name, channel_topic):
    try:
        response = client.conversations_create(name=channel_name, is_private=False)

        channel_id = response["channel"]["id"]
        print(channel_id)

        response = client.conversations_setPurpose(
            channel=channel_id, purpose=channel_topic
        )
        response = client.conversations_setTopic(
            channel=channel_id, topic=channel_topic
        )

        response = client.chat_postMessage(
            channel="general", text=f"New change created on channel <#{channel_id}>"
        )

        response = client.chat_postMessage(
            channel=channel_id, text=f"Welcome, @mattstibbs"
        )
    except Exception as e:
        print(e)


def invite_to_channel(channel_id, list_of_users):
    for user in list_of_users:
        response = client.conversations_invite(channel=channel_id, users=f"{user}")
        print(response)


# @slack_events_adapter.on("app_mention")
# def app_mention(event_data):
#     print(event_data)


@app.route("/commands", methods=["POST"])
def process_command():
    logging.debug(request.form["command"])
    logging.debug(request.form["text"])
    logging.debug(request.form)

    user_id = request.form["user_id"]
    print(user_id)

    change_ephemeral = client.chat_postEphemeral(
        as_user=True,
        channel=request.form["channel_id"],
        user=user_id,
        text="I'm the Change Bot and I'm here to help you create a change!",
        blocks=[
            {
                "type": "actions",
                "block_id": "actions1",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Create Change"},
                        "value": "create_change",
                        "action_id": "create_change",
                        "style": "primary",
                    }
                ],
            }
        ],
    )

    print(change_ephemeral)

    CHANGES[user_id] = {
        "conversation": request.form["channel_id"],
        "message_ts": "",
        "change": {},
    }

    print(CHANGES)

    return make_response("", 200)


@app.route("/interactive", methods=["POST"])
def process_interactive():

    logging.debug(request.form)
    message_action = json.loads(request.form["payload"])
    user_id = message_action["user"]["id"]

    if message_action["type"] == "block_actions":
        # Add the message_ts to the user's order info
        message_ts = message_action["container"]["message_ts"]
        response_url = message_action["response_url"]
        CHANGES[user_id]["message_ts"] = message_ts

        print(CHANGES)
        print(response_url)

        view_open = client.views_open(
            trigger_id=message_action["trigger_id"],
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
                            "action_id": "txt_change_description",
                            "multiline": False,
                        },
                        "block_id": "change_description",
                        "label": {
                            "type": "plain_text",
                            "text": "Description",
                            "emoji": False,
                        },
                    },
                ],
            },
        )

        r = requests.post(response_url, data={"delete_original": True})

        # return jsonify(
        #     {
        #         "response_type": "ephemeral",
        #         "text": "",
        #         "replace_original": True,
        #         "delete_original": True,
        #     }
        # )

    elif message_action["type"] == "view_submission":

        logging.debug(pformat(request.form.to_dict()))

        state_values = message_action["view"]["state"]["values"]

        pprint(state_values)

        change_no = state_values["change_no"]["txt_change_no"]["value"]
        change_description = state_values["change_description"][
            "txt_change_description"
        ]["value"]

        # TODO: Check whether the channel already exists.

        # Create the new channel and set purpose / topic
        new_channel = client.conversations_create(name=f"111-change-{change_no}")
        new_channel_id = new_channel["channel"]["id"]
        client.conversations_setPurpose(
            channel=new_channel_id, purpose=change_description
        )
        client.conversations_setTopic(channel=new_channel_id, topic=change_description)

        print(new_channel)

        # Invite the original user into the channel
        client.conversations_invite(channel=new_channel_id, users=[user_id])

        client.chat_postMessage(
            as_user=True,
            channel=CHANGES[user_id]["conversation"],
            text=f"<@{user_id}> created <#{new_channel['channel']['id']}>\n>*{change_description}*",
        )

    return make_response("", 200)


user_list = get_user_list()

# Start the server on port 5000
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
