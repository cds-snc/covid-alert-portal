#!/bin/bash

echo "Compile CSS"
python manage.py sass profiles/static/scss/styles.scss profiles/static/css/

# If DJANGO_DEBUG isn't 'True' (defaults to 'False'), we need copy the static files over

echo "Collect static files"
python manage.py collectstatic --noinput -i scss

echo "Compiling translations"
pipenv run python manage.py compilemessages

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Create default superuser if variables are set
echo "Check if creating default super user"
python manage.py createdefaultsuperuser

# Start server
echo "Starting server"
uwsgi --http :8000 --module portal.wsgi --static-map /static=/code/staticfiles --enable-threads
