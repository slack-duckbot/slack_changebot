import logging
from datetime import date

from jira import JIRA

from app import app

if app.config["ENABLE_JIRA_INTEGRATION"]:
    logging.debug("Creating Jira client")
    jira_options = {"server": app.config["JIRA_SERVER"]}
    try:
        truncated_pwd = app.config["JIRA_PASSWORD"][-4:]
        logging.debug(app.config["JIRA_SERVER"])
        logging.debug(jira_options)
        logging.debug(truncated_pwd)
        jira_client = JIRA(
            options=jira_options,
            basic_auth=(app.config["JIRA_USERNAME"], app.config["JIRA_PASSWORD"]),
        )
        logging.debug("Jira client created")
    except Exception as e:
        logging.debug(f"Issue creating Jira client: {e}")


def create_jira_release(change_number, user_name, description):

    if app.config["ENABLE_JIRA_INTEGRATION"]:
        today = date.today()
        change_name = app.config["JIRA_PREFIX"] + change_number
        version = jira_client.create_version(
            name=change_name,
            project=app.config["JIRA_PROJECT_KEY"],
            startDate=today.strftime("%Y-%m-%d"),
            description=description,
        )
        version_id = version.id
        return f"{app.config['JIRA_SERVER']}/projects/{app.config['JIRA_PROJECT_KEY']}/versions/{version_id}"
    else:
        return False
