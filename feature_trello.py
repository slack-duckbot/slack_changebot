import logging
from pprint import pprint, pformat

import requests

from settings import (
    ENABLE_TRELLO_INTEGRATION,
    TRELLO_PREFIX,
    TRELLO_LIST_IDS,
    TRELLO_API_KEY,
    TRELLO_TOKEN,
)

TRELLO_API = "https://api.trello.com/1"


def create_trello_cards(change_number, user_name, description, release_notes):
    if ENABLE_TRELLO_INTEGRATION:
        logging.debug("Creating Trello card")
        change_name = f"{TRELLO_PREFIX}{change_number} - {description}"

        card_description = f"_Change created by {user_name}_"
        if release_notes:
            card_description = release_notes + "\n\n\n" + card_description

        for list_id in TRELLO_LIST_IDS:
            response = requests.post(
                f"{TRELLO_API}/cards",
                data={
                    "name": change_name,
                    "pos": "bottom",
                    "desc": card_description,
                    "idList": list_id,
                    "key": TRELLO_API_KEY,
                    "token": TRELLO_TOKEN,
                },
            )
            short_url = response.json()["shortUrl"]

        return short_url
    else:
        return None
