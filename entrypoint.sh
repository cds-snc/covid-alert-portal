#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# If running in 'production' mode, we need these

# echo "Compile CSS"
python manage.py sass profiles/assets/scss/ profiles/static/css/

# echo "Collect static files"
python manage.py collectstatic --noinput

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000