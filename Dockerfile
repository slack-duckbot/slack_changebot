FROM python:3.9.2 as duckbot_base
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY app /code/app

FROM duckbot_base as duckbot_prod
WORKDIR /code
EXPOSE 8000
ENTRYPOINT ["gunicorn", "--workers=1", "-b", "0.0.0.0:8000", "app:app", "--log-file", "-"]

FROM duckbot_base as duckbot_worker
WORKDIR /code
COPY worker/rq_settings.py /code/worker/rq_settings.py
ENTRYPOINT ["rq", "worker", "-c", "worker.rq_settings"]

FROM duckbot_base as duckbot_dev
WORKDIR /code
COPY requirements-dev.txt /code/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements-dev.txt
EXPOSE 5000
CMD ["python", "-m", "flask", "run", "--eager-loading"]
