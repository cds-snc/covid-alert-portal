#!/usr/bin/env bash
sleep 5
# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Create default superuser if variables are set
echo "Check if creating default super user"
python manage.py createdefaultsuperuser

# add the crontab
crontab cronjobs.txt

# set desired environment variables globally so that the cronjob can access them
env | grep DATABASE_URL >> /etc/environment

# Run supervisor
/usr/bin/supervisord -nc /code/supervisord.conf
