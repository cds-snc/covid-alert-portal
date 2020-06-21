web: python manage.py migrate; python manage.py sass profiles/assets/scss/ profiles/static/css/; python manage.py collectstatic --noinput; gunicorn portal.wsgi --log-file -
