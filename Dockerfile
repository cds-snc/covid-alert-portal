# Dockerfile

# Pull base image
FROM python:3.8-slim

ARG GITHUB_SHA_ARG
ENV GITHUB_SHA=$GITHUB_SHA_ARG

# Installs gettext utilities required to makemessages and compilemessages
RUN apt-get update && apt-get install -y --no-install-recommends \
	gettext \
	make \
	build-essential \
	mime-support \
	git \
	&& rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Install pipenv
RUN pip install 'pipenv==2018.11.26' uwsgi

# Install dependencies
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system --dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY . /code

# Build static files

RUN python manage.py sass profiles/static/scss/styles.scss profiles/static/css/

RUN python manage.py collectstatic --noinput -i scss

RUN python manage.py compilemessages

RUN groupadd -r django && useradd --no-log-init -M -g django django

RUN chown -R django:django /code

USER django:django

EXPOSE 8000

CMD ["./entrypoint.sh"]
