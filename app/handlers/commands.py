import logging

from flask import request, make_response

from app import app
from app.views.create_change import show_view_create_change
from app.views import rename_change
from app.helpers.slack import get_next_change_number, verify_request
from app.helpers.redis import redis_q
from app.workflows import change_going_live


@app.route("/commands", methods=["POST"])
def process_command():
    if not verify_request(request):
        return make_response("", 403)

    form = request.form
    command_text = form["text"]
    logging.debug(f"Command received: {request.form['command']} {command_text}")

    trigger_id = request.form["trigger_id"]

    if command_text == "new":
        show_view_create_change(trigger_id, form)
        return make_response("", 200)

    elif command_text == "next":
        next_change_number = get_next_change_number()
        return make_response(
            f"The next available Slack change channel is: *{next_change_number}*\n*MAKE SURE YOU CHECK THE CHANGES TRELLO BOARD TOO* :eyes: https://trello.com/b/cj665kSN/111-ol-release-board",
            200,
        )

    elif command_text == "rename":
        redis_q.enqueue(rename_change.rename_channel, request.form)
        return make_response("", 200)

    elif command_text == "release":
        redis_q.enqueue(change_going_live.change_going_live, request.form)
        return make_response("", 200)

    else:
        return make_response(
            f"*{command_text}* command is not supported currently.", 200
        )
