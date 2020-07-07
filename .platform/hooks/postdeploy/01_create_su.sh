#!/bin/bash
source /var/app/venv/*/bin/activate
echo "Create Super User if specified"
python manage.py createdefaultsuperuser
