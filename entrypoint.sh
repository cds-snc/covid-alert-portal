#!/usr/bin/env bash
sleep 5
# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Create default superuser if variables are set
echo "Check if creating default super user"
python manage.py createdefaultsuperuser

# Compile the protobufs (manually add more steps here if necessary)
protoc -I outbreaks/protobufs --python_out=outbreaks/protobufs outbreaks/protobufs/outbreak.proto

# Start server
echo "Starting server"
if [[ ${DJANGO_ENV} == 'development' ]]; then
	python manage.py runserver 0.0.0.0:8000
else
	uwsgi --http :8000 --master --module portal.wsgi --static-map /static=/code/staticfiles --enable-threads --processes 2
fi
