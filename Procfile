web: gunicorn --workers=1 --timeout=120 --preload app:app --log-file -
worker: rq worker --url $REDIS_URL
