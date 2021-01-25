web: gunicorn --workers=1 app:app --log-level=debug --log-file --timeout=60 -
worker: rq worker --url $REDIS_URL