from slack import WebClient
from settings import SLACK_TOKEN

def get_slack_client():
    return WebClient(token=SLACK_TOKEN)


def get_user_list():
    response = get_slack_client().users_list()

    members = response["members"]
    user_ids = []

    for member in members:
        user = {"user_id": member["id"], "name": member["name"]}
        user_ids.append(user)

    return user_ids


def does_channel_exist(channel_name):
    response = get_slack_client().channels_list()

    channels = response["channels"]

    results = [channel for channel in channels if channel["name"] == channel_name]
    print(results)
    if len(results) > 0:
        return True
    else:
        return False