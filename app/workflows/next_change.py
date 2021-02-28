from app.helpers import slack as sl
from app.helpers.slack import get_next_change_number
import requests
import logging

client = sl.get_slack_client()


def next_change(response_url):
    logging.info("Starting Workflow: Next Change")
    next_change_number = get_next_change_number()
    payload = {
        "text": f"The next available Slack change channel is: *{next_change_number}*\n*MAKE SURE YOU CHECK THE CHANGES TRELLO BOARD TOO* :eyes: https://trello.com/b/cj665kSN/111-ol-release-board",
        "response_type": "ephemeral",
    }
    requests.post(response_url, json=payload)
    logging.info("Finished Workflow: Next Change")
