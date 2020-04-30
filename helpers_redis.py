import redis
import rq

import settings

# Set up a redis connection to be used for the async worker queue
redis_q_conn = redis.from_url(settings.REDIS_URL, db=0)
redis_q = rq.Queue(connection=redis_q_conn)

# Set up a redis connection to db 1 to be used for de-duplicating inbound requests
redis_conn = redis.from_url(settings.REDIS_URL, db=1)


def request_processed(event_id):
    redis_conn.set(event_id, 1)


def request_previously_responded(event_id):
    redis_conn.get(event_id)
