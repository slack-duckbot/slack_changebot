import hashlib
import hmac
import logging
import time

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

    change_number_list = []

    for change in change_channel_list:
        try:
            channel_name = change[0]
            change_number_list.append(int(channel_name.rpartition("-")[-1]))
        except ValueError as e:
            logging.error(f"Skipping invalid change number {channel_name} ({e})")
            continue

    sorted_change_list = sorted(change_number_list, reverse=True)

    next_change_number = next(iter(sorted_change_list)) + 1

    return next_change_number


def verify_request(request):
    slack_signing_secret = bytes(app.config["SLACK_SIGNING_SECRET"], "utf-8")

    request_body = request.get_data().decode()

    slack_request_timestamp = request.headers["X-Slack-Request-Timestamp"]
    slack_signature = request.headers["X-Slack-Signature"]

    # Check that the request is no more than 60 seconds old
    if (int(time.time()) - int(slack_request_timestamp)) > 60:
        logging.warning("Verification failed. Request is out of date.")
        return False

    # Create a basestring by concatenating the version, the request timestamp, and the request body
    basestring = f"v0:{slack_request_timestamp}:{request_body}".encode("utf-8")

    # Hash the basestring using your signing secret, take the hex digest, and prefix with the version number
    my_signature = (
        "v0=" + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()
    )

    # Compare the resulting signature with the signature on the request to verify the request
    if hmac.compare_digest(my_signature, slack_signature):
        return True
    else:
        logging.warning("Verification failed. Signature invalid.")
        return False


def is_change_channel(channel_name, change_channel_prefix=None):
    prefix = (
        change_channel_prefix
        if change_channel_prefix
        else app.config["SLACK_CHANGE_CHANNEL_PREFIX"]
    )

    if channel_name.startswith(prefix):
        return True
    else:
        return False


def get_change_number_from_channel_name(channel_name):
    return int(channel_name.rpartition("-")[-1])

