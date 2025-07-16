#!/usr/bin/env bash

source .env

python manage.py makemigrations
python manage.py migrate

# start processing tasks in the background
# python manage.py process_tasks &

# TODO: change this so it runs from gunicorn - at present gunicorn times out
# on any/every request

python manage.py runserver_plus 0.0.0.0:${PORT} --cert /tmp/cert
#gunicorn -b 0.0.0.0:9100 -w 1 auctionhouse.wsgi:application
