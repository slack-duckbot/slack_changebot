web: gunicorn --workers=2 app:app --log-file -
worker: rq worker --url $REDIS_URL