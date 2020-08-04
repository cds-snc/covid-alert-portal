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
uwsgi --http :8000 --master --module portal.wsgi --static-map /static=/code/staticfiles --enable-threads --processes 2
