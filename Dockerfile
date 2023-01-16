FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y libpq-dev python3-dev python-dev python-psycopg2 python3-psycopg2 gcc qrencode cron

ADD requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /bank_project
COPY ./bank_project /bank_project


COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
