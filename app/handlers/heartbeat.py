from app import app


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return "", 200
