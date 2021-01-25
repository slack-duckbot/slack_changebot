web: gunicorn --workers=1 app:app --preload --log-file -
worker: rq worker --url $REDIS_URL