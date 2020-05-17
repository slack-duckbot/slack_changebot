from slack import WebClient
from app import app


def get_slack_client():
    return WebClient(token=app.config["SLACK_TOKEN"])


client = get_slack_client()


def get_full_conversations_list():
    change_channel_list = []

    response = client.conversations_list(limit=1000, types="public_channel")

    cursor = response["response_metadata"]["next_cursor"]

    channels = response["channels"]

    change_channel_list.extend(extract_change_channels(channels))

    while cursor != "":
        response = client.conversations_list(
            limit=1000, types="public_channel", cursor=cursor
        )
        cursor = response["response_metadata"]["next_cursor"]

        channels = response["channels"]
        change_channel_list.extend(extract_change_channels(channels))

    return change_channel_list


def get_user_list():
    response = client.users_list()

    members = response["members"]
    user_ids = []

    for member in members:
        user = {"user_id": member["id"], "name": member["name"]}
        user_ids.append(user)

    return user_ids


def does_channel_exist(channel_name):
    channels = get_full_conversations_list()

    exists = next((channel for channel in channels if channel[0] == channel_name), None)

    return True if exists else False


def extract_change_channels(channels):
    channel_list = []
    for channel in channels:
        if channel["name"].startswith(app.config["SLACK_CHANGE_CHANNEL_PREFIX"]):
            channel_list.append((channel["name"], channel["id"]))
    return channel_list


def get_next_change_number():

    change_channel_list = get_full_conversations_list()

    sorted_channel_list = sorted(change_channel_list, key=lambda i: i[0])

    if len(sorted_channel_list) > 0:
        most_recent_channel = sorted_channel_list[-1]
        next_change_number = (
            int(most_recent_channel[0].rsplit(sep="-", maxsplit=1)[-1]) + 1
        )

        return next_change_number
