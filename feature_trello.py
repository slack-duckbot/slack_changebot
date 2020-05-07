import requests
from pprint import pprint, pformat
from settings import ENABLE_TRELLO_INTEGRATION, TRELLO_PREFIX, TRELLO_LIST_ID

TRELLO_API = "https://api.trello.com/1"


def create_trello_release(change_number, user_name, description, release_notes):
    if ENABLE_TRELLO_INTEGRATION:
        change_name = f"{TRELLO_PREFIX}{change_number} - {description}"

        card_id = requests.post(
            f"{TRELLO_API}/cards",
            data={
                "name": change_name,
                "pos": "bottom",
                "desc": release_notes,
                "idList": TRELLO_LIST_ID,
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
            },
        )

        return f"https://trello.com/c/{card_id}"
    else:
        return False
