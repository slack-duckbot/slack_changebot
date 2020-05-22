from flask import json
from flask import request, make_response

from app import app
from app.features.release_notes import update_release_notes
from app.helpers.slack import does_channel_exist, get_slack_client, verify_request
from app.helpers.redis import redis_q
from app.helpers import general
from app.workflows import create_change

from app.views.edit_change import show_view_edit_change

client = get_slack_client()


@app.route("/interactive", methods=["POST"])
def process_interactive():

    if not verify_request(request):
        return make_response("", 403)

    message_payload = json.loads(request.form["payload"])
    user_id = message_payload["user"]["id"]
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

            if metadata["change_summary"] != change_summary:
                redis_q.enqueue(
                    client.conversations_setPurpose,
                    channel=metadata["channel_id"],
                    purpose=change_summary,
                )

                redis_q.enqueue(
                    client.conversations_setTopic,
                    channel=metadata["channel_id"],
                    topic=change_summary,
                )

        if callback_id == "create_change_modal":

            state_values = message_payload["view"]["state"]["values"]
            change_number = state_values["change_no"]["txt_change_no"]["value"]
            metadata = json.loads(message_payload["view"]["private_metadata"])
            channel_id = metadata["channel_id"]
            user_id = message_payload["user"]["id"]
            user_name = message_payload["user"]["name"]

            if not general.represents_an_int(change_number):
                return {
                    "response_action": "errors",
                    "errors": {"change_no": "Must be a number"},
                }

            new_channel_name = (
                f"{app.config['SLACK_CHANGE_CHANNEL_PREFIX']}{change_number}"
            )

            # Check to see if channel already exists, return an error if so
            if does_channel_exist(new_channel_name):
                return {
                    "response_action": "errors",
                    "errors": {
                        "change_no": "A channel already exists with this change number"
                    },
                }

            redis_q.enqueue(create_change.create_change, message_payload)

            # client.chat_postEphemeral(
            #     user=user_id, channel=user_name, text="Creating a change for you...",
            # )

        if callback_id == "rename_conversation_modal":
            state_values = message_payload["view"]["state"]["values"]
            metadata = json.loads(message_payload["view"]["private_metadata"])
            new_name = state_values["new_name"]["txt_new_name"]["value"]
            channel_id = metadata["channel_id"]
            client.conversations_rename(channel=channel_id, name=new_name)

        return make_response("", 200)
