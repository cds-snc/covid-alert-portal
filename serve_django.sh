#!/usr/bin/env bash

# Start the appropriate server
echo "Starting server"
if [[ ${DJANGO_ENV} == 'development' ]]; then
	python manage.py runserver 0.0.0.0:8000;
else
	portal.wsgi --static-map /static=/code/staticfiles --enable-threads --processes 2
fi
