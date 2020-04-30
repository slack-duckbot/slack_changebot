import os

from dotenv import load_dotenv

load_dotenv(override=True)


def config_string_to_bool(setting):
    if setting.lower() in ("true", "yes", "on"):
        return True
    else:
        return False


SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_CHANGES_CHANNEL = os.environ["SLACK_CHANGES_CHANNEL"]
SLACK_CHANGE_CHANNEL_PREFIX = os.environ["SLACK_CHANGE_CHANNEL_PREFIX"]

# Jira configuration
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_PASSWORD = os.environ["JIRA_PASSWORD"]
JIRA_SERVER = os.environ["JIRA_SERVER"]
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]

# Feature toggles
ENABLE_JIRA_INTEGRATION = config_string_to_bool(os.environ["ENABLE_JIRA_INTEGRATION"])
ENABLE_RELEASE_NOTES = config_string_to_bool(os.environ["ENABLE_RELEASE_NOTES"])
