web: gunicorn --workers=1 --worker-class gevent app:app --log-file -
worker: rq worker --url $REDIS_URL
