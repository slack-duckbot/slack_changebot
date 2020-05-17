import logging

import requests

from app import app

TRELLO_API = "https://api.trello.com/1"


def create_trello_cards(change_number, user_name, description, release_notes):
    if app.config["ENABLE_TRELLO_INTEGRATION"]:
        logging.debug("Creating Trello card")
        change_name = f"{app.config['TRELLO_PREFIX']}{change_number} - {description}"

        card_description = f"_Change created by {user_name}_"
        if release_notes:
            card_description = release_notes + "\n\n\n" + card_description

        for list_id in app.config["TRELLO_LIST_IDS"]:
            response = requests.post(
                f"{TRELLO_API}/cards",
                data={
                    "name": change_name,
                    "pos": "bottom",
                    "desc": card_description,
                    "idList": list_id,
                    "key": app.config["TRELLO_API_KEY"],
                    "token": app.config["TRELLO_TOKEN"],
                },
            )
            short_url = response.json()["shortUrl"]

        return short_url
    else:
        return None
