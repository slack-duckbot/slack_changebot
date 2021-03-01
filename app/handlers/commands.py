import logging
import threading

from flask import request, make_response

from app import app
from app.views.create_change_start import show_view_create_change_start
from app.views import rename_change
from app.helpers.slack import verify_request, get_next_change_number
from app.helpers.redis import redis_q
from app.workflows import change_going_live, next_change


# Using threads within these methods to try and keep the response time to the Slack API as low as possible


@app.route("/commands", methods=["POST"])
def process_command():
    if not verify_request(request):
        return make_response("", 403)

    form = request.form
    command_text = form["text"]
    logging.debug(f"Command received: {request.form['command']} {command_text}")

    trigger_id = request.form["trigger_id"]

    if command_text == "new":
        # We show an initial start view so that we can give enough time to perform slow actions async.
        # This is to help us manage Slack's strict timeout rules.
        thread_1 = threading.Thread(target=get_next_change_number)

        thread_2 = threading.Thread(
            target=show_view_create_change_start,
            args=(
                trigger_id,
                form,
            ),
        )
        thread_1.start()
        thread_2.start()
        return make_response("", 200)

    elif command_text == "next":
        response_url = request.form["response_url"]
        thread = threading.Thread(target=next_change.next_change, args=(response_url,))
        thread.start()
        return make_response("", 200)

    elif command_text == "rename":
        thread = threading.Thread(
            target=redis_q.enqueue,
            args=(rename_change.rename_channel, request.form),
        )
        thread.start()
        return make_response("", 200)

    elif command_text == "release":
        thread = threading.Thread(
            target=redis_q.enqueue,
            args=(change_going_live.change_going_live, request.form),
        )
        thread.start()
        return make_response("", 200)

    else:
        return make_response(
            f"*{command_text}* command is not supported currently.", 200
        )
