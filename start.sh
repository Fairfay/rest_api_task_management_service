#!/bin/bash

poetry run python manage.py check

poetry run python manage.py collectstatic --noinput

poetry run python manage.py migrate

poetry run gunicorn -c gunicorn.conf.py