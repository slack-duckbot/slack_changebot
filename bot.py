import os
import pprint
import slack
from flask import jsonify, json
from flask import Flask
from flask import request, Response, make_response
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ.get(
    "SLACK_SIGNING_SECRET", "b6acda85de7e145fa620cb2de2d6cd05"
)

SLACK_TOKEN = os.environ.get(
    "SLACK_TOKEN", "xoxb-2352877446-1054758032930-lU3pGZaCBCUcW098RGyvjnKP"
)

slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/events", app)

client = slack.WebClient(token=SLACK_TOKEN)

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
    for user in list_of_usewrs:
        response = client.conversations_invite(channel=channel_id, users=f"{user}")
        print(response)


@slack_events_adapter.on("app_mention")
def app_mention(event_data):
    print(event_data)


@app.route("/commands", methods=["POST"])
def process_command():
    print(request.form["command"])
    print(request.form["text"])
    print(request.form)

    user_id = request.form["user_id"]
    print(user_id)

    change_ephemeral = client.chat_postEphemeral(
        as_user=True,
        channel=request.form["channel_id"],
        user=user_id,
        text="I'm the Change Bot and I'm here to help you create a change!",
        attachments=[
            {
                "text": "",
                "callback_id": user_id + "change_request_form",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "create_change",
                        "text": "Create Change",
                        "type": "button",
                        "value": "create_change",
                    }
                ],
            }
        ],
    )

    print(change_ephemeral)

    CHANGES[user_id] = {
        "change_channel": request.form["channel_id"],
        "message_ts": "",
        "change": {},
    }

    print(CHANGES)

    return make_response("", 200)


@app.route("/interactive", methods=["POST"])
def process_interactive():

    print(request.form.to_dict())

    message_action = json.loads(request.form["payload"])

    user_id = message_action["user"]["id"]

    if message_action["type"] == "interactive_message":
        # Add the message_ts to the user's order info
        CHANGES[user_id]["message_ts"] = message_action["message_ts"]

        print(CHANGES)

        view_response = client.views_open(
            trigger_id=message_action["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "create_change_modal",
                "title": {"type": "plain_text", "text": "Create change"},
                "blocks": [
                    {
                        "type": "input",
                        "label": {"type": "plain_text", "text": "Input label"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "change_number",
                            "multiline": False,
                        },
                        "optional": False,
                    }
                ],
                "close": {"type": "plain_text", "text": "Cancel"},
                "submit": {"type": "plain_text", "text": "Create Channel"},
            },
        )

    elif message_action["type"] == "view_submission":
        print(CHANGES[user_id]["change_channel"])
        print(CHANGES[user_id]["message_ts"])
        chat_delete = client.chat_delete(
            channel=CHANGES[user_id]["change_channel"],
            ts=CHANGES[user_id]["message_ts"],
            as_user=True,
        )

        print(chat_delete)

    return make_response("", 200)


user_list = get_user_list()

# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=3000, debug=True)
