web: gunicorn --workers=1 bot:app --log-file -
worker: rq worker --url $REDIS_URL