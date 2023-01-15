#!/bin/sh

python manage.py check --deploy
python manage.py collectstatic --noinput
python manage.py migrate --no-input
#python manage.py seed_data
gunicorn bank_project.asgi:application -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker
