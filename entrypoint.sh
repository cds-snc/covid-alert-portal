#!/usr/bin/env bash
sleep 5
# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Create default superuser if variables are set
echo "Check if creating default super user"
python manage.py createdefaultsuperuser

# Start server
echo "Starting server"
if [[ ${DJANGO_ENV} == 'development' ]]; then
	python manage.py runserver 0.0.0.0:8000
else
	uwsgi --http :8000 --master --module portal.wsgi --static-map /static=/code/staticfiles --enable-threads --processes 2
fi
