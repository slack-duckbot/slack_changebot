import logging

from app import app
from app.helpers import slack as sl

client = sl.get_slack_client()


def release_change(form):
    channel_name = form["channel_name"]

    if not sl.is_change_channel(channel_name):
        logging.debug("Not a valid change channel")
        return False
