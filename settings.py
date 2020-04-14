import os

from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
