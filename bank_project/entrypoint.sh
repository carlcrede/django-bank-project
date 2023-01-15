#!/bin/sh

echo "${RTE} Runtime Environment - Running entrypoint."

if [ "$RTE" = "dev" ]; then
    # echo "Performing python manage.py migrate"
    # python manage.py migrate
    echo "Performing python manage.py makemigrations --merge"
    python manage.py makemigrations --merge
    echo "Performing python manage.py migrate --noinput"
    python manage.py migrate --noinput
    python manage.py seed_data
    echo "Performing python manage.py runserver 8000"
    python manage.py runserver 0.0.0.0:8000

elif [ "$RTE" = "test" ]; then

    echo "This is test."

elif [ "$RTE" = "prod" ]; then

    python manage.py check --deploy
    python manage.py collectstatic --noinput
    gunicorn dj_deploy.asgi:application -b 0.0.0.0:8080 -k uvicorn.workers.UvicornWorker

fi