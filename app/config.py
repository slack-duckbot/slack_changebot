import json
import os

from dotenv import load_dotenv

load_dotenv(override=True)


def config_string_to_bool(setting):
    if setting.lower() in ("true", "yes", "on"):
        return True
    else:
        return False


def parse_list_from_env_var(env_var):
    var_list = json.loads(env_var)
    return var_list


class DefaultConfig:
    DEBUG = False
    TESTING = False

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

    SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
    SLACK_TOKEN = os.environ["SLACK_TOKEN"]
    SLACK_CHANGES_CHANNEL = os.environ["SLACK_CHANGES_CHANNEL"]
    SLACK_CHANGE_CHANNEL_PREFIX = os.environ["SLACK_CHANGE_CHANNEL_PREFIX"]
    SLACK_USER_TOKEN = os.environ["SLACK_USER_TOKEN"]

    # Jira configuration
    JIRA_USERNAME = os.environ["JIRA_USERNAME"]
    JIRA_PASSWORD = os.environ["JIRA_PASSWORD"]
    JIRA_SERVER = os.environ["JIRA_SERVER"]
    JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]
    JIRA_PREFIX = os.environ["JIRA_PREFIX"]

    # Trello configuration
    TRELLO_API_KEY = os.environ["TRELLO_API_KEY"]
    TRELLO_TOKEN = os.environ["TRELLO_TOKEN"]
    TRELLO_LIST_IDS = parse_list_from_env_var(os.environ["TRELLO_LIST_IDS"])
    TRELLO_PREFIX = os.environ["TRELLO_PREFIX"]

    # Feature toggles
    ENABLE_JIRA_INTEGRATION = config_string_to_bool(
        os.environ["ENABLE_JIRA_INTEGRATION"]
    )
    ENABLE_TRELLO_INTEGRATION = config_string_to_bool(
        os.environ["ENABLE_TRELLO_INTEGRATION"]
    )
    ENABLE_RELEASE_NOTES = config_string_to_bool(os.environ["ENABLE_RELEASE_NOTES"])


class DevelopmentConfig(DefaultConfig):
    DEBUG = True


class TestingConfig(DefaultConfig):
    TESTING = True


class ProductionConfig(DefaultConfig):
    pass
