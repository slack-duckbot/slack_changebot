# Python module containing RQ (Redis Queue) work settings.
#
# A worker is a Python process that typically runs in the background and
# exists solely as a work horse to perform lengthy or blocking tasks that
# you don't want to perform inside web processes.
#
# Start a worker using:
# $ rq worker -c rq_settings
import os

REDIS_URL = os.environ["REDIS_URL"]
QUEUES = ["default"]
