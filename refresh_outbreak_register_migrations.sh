#!/usr/bin/env bash

# Temporary - rollback/re-generate/re-run migrations
python manage.py migrate outbreaks zero
python manage.py migrate register zero

# This one doesn't get deleted for some reason
python manage.py dbshell -- "DELETE FROM django_migrations where app='register'"

# Delete existing migrations
find . -path "./register/migrations/*.py" -not -name "__init__.py" -delete
find . -path "./outbreaks/migrations/*.py" -not -name "__init__.py" -delete

# Generate new ones
python manage.py makemigrations