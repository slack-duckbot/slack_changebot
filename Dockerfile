FROM python:3.8

WORKDIR /usr/src/slack_changebot
COPY requirements.txt requirements-dev.txt /usr/src/slack_changebot/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
