#!/bin/sh
set -e

poetry run python manage.py check

poetry run python manage.py makemigrations

poetry run python manage.py migrate

exec poetry run gunicorn -c gunicorn.conf.py