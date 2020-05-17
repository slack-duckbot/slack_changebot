web: gunicorn --workers=1 app:app --log-file -
worker: rq worker --url $REDIS_URL