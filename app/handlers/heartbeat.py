from app import app

from app.helpers.redis import redis_q


def rq_worker():
    return True


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    redis_q.enqueue(rq_worker)
    return "", 200
