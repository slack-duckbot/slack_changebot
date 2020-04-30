from slack import WebClient
from settings import SLACK_TOKEN, SLACK_CHANGE_CHANNEL_PREFIX


def get_slack_client():
    return WebClient(token=SLACK_TOKEN)


def get_next_change_number():
    response = get_slack_client().channels_list()
    channels = response["channels"]

    channel_list = []

    for channel in channels:
        if channel["name"].startswith(SLACK_CHANGE_CHANNEL_PREFIX):
            channel_list.append((channel["name"], channel["id"]))

    sorted_channel_list = sorted(channel_list, key=lambda i: i[0])
    most_recent_channel = sorted_channel_list[-1]
    next_change_number = int(most_recent_channel[0].rsplit(sep="-", maxsplit=1)[-1]) + 1

    return next_change_number
