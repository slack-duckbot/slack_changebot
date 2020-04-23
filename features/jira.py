from datetime import date
from jira import JIRA
from pprint import pprint, pformat
import settings

if settings.CREATE_JIRA_VERSIONS == "True":
    jira_options = {
        'server': settings.JIRA_SERVER
    }
    jira = JIRA(options=jira_options, basic_auth=(settings.JIRA_USERNAME, settings.JIRA_PASSWORD))
      
def create_jira_release(change_number, user_name, description):
    if settings.CREATE_JIRA_VERSIONS == "True":
        today = date.today()
        change_name = "C" + change_number

        version = jira.create_version(
            name=change_name,
            project=settings.JIRA_PROJECT_KEY,
            startDate=today.strftime("%Y-%m-%d"),
            description=description
        )
        version_id = version.id
        return f"{settings.JIRA_SERVER}/projects/{settings.JIRA_PROJECT_KEY}/versions/{version_id}"
    else:
        return False

