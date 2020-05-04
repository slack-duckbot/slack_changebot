from slack import WebClient
from settings import SLACK_TOKEN, SLACK_CHANGE_CHANNEL_PREFIX


def get_slack_client():
    return WebClient(token=SLACK_TOKEN)


def extract_change_channels(channels):
    channel_list = []
    for channel in channels:
        if channel["name"].startswith(SLACK_CHANGE_CHANNEL_PREFIX):
            channel_list.append((channel["name"], channel["id"]))
    return channel_list


def get_next_change_number():
    change_channel_list = []

    response = get_slack_client().conversations_list(limit=1000, types="public_channel")

    cursor = response["response_metadata"]["next_cursor"]

    channels = response["channels"]

    change_channel_list.extend(extract_change_channels(channels))

    while cursor != "":
        response = get_slack_client().conversations_list(
            limit=1000, types="public_channel", cursor=cursor
        )
        cursor = response["response_metadata"]["next_cursor"]

        channels = response["channels"]
        change_channel_list.extend(extract_change_channels(channels))

    sorted_channel_list = sorted(change_channel_list, key=lambda i: i[0])

    if len(sorted_channel_list) > 0:
        most_recent_channel = sorted_channel_list[-1]
        next_change_number = (
            int(most_recent_channel[0].rsplit(sep="-", maxsplit=1)[-1]) + 1
        )

        return next_change_number
