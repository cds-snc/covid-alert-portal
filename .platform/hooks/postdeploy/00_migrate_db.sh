#!/bin/bash
source /var/app/venv/*/bin/activate
echo "Migrate DB"
python manage.py migrate --noinput
