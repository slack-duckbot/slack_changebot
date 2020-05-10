from datetime import date
from jira import JIRA
from pprint import pprint, pformat
from settings import (
    ENABLE_JIRA_INTEGRATION,
    JIRA_SERVER,
    JIRA_USERNAME,
    JIRA_PASSWORD,
    JIRA_PROJECT_KEY,
    JIRA_PREFIX,
)

if ENABLE_JIRA_INTEGRATION:
    jira_options = {"server": JIRA_SERVER}
    jira_client = JIRA(options=jira_options, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))


def create_jira_release(change_number, user_name, description):
    if ENABLE_JIRA_INTEGRATION:
        today = date.today()
        change_name = JIRA_PREFIX + change_number
        version = jira_client.create_version(
            name=change_name,
            project=JIRA_PROJECT_KEY,
            startDate=today.strftime("%Y-%m-%d"),
            description=description,
        )
        version_id = version.id
        return f"{JIRA_SERVER}/projects/{JIRA_PROJECT_KEY}/versions/{version_id}"
    else:
        return False
