#!/bin/sh

python manage.py check --deploy
python manage.py collectstatic --noinput
python manage.py migrate --no-input
python manage.py seed_data --skip-checks
python manage.py rqworker --with-scheduler &
python manage.py crontab add &
gunicorn bank_project.asgi:application -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker
