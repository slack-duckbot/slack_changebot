web: gunicorn --workers=1 --timeout 120 --loglevel debug app:app --log-file -
worker: rq worker --url $REDIS_URL
