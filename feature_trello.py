import logging

import requests
from pprint import pprint, pformat
from settings import (
    ENABLE_TRELLO_INTEGRATION,
    TRELLO_PREFIX,
    TRELLO_LIST_ID,
    TRELLO_API_KEY,
    TRELLO_TOKEN,
)

TRELLO_API = "https://api.trello.com/1"


def create_trello_card(change_number, user_name, description, release_notes):
    if ENABLE_TRELLO_INTEGRATION:
        logging.debug("Creating Trello card")
        change_name = f"{TRELLO_PREFIX}{change_number} - {description}"

        card_description = f"_Change created by {user_name}_"
        if release_notes:
            card_description = release_notes + "\n\n\n" + card_description

        response = requests.post(
            f"{TRELLO_API}/cards",
            data={
                "name": change_name,
                "pos": "bottom",
                "desc": card_description,
                "idList": TRELLO_LIST_ID,
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
            },
        )

        return response.json()["shortUrl"]
    else:
        return False
