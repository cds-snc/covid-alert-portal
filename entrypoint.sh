#!/bin/bash

echo "Compile CSS"
python manage.py sass profiles/assets/scss/ profiles/static/css/

# If DJANGO_DEBUG isn't 'True' (defaults to 'False'), we need copy the static files over

echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
