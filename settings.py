import os

from dotenv import load_dotenv

load_dotenv(override=True)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]


# Feature toggles
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_PASSWORD = os.environ["JIRA_PASSWORD"]
JIRA_SERVER = os.environ["JIRA_SERVER"]
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]
CREATE_JIRA_VERSIONS = os.environ["CREATE_JIRA_VERSIONS"]