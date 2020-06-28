# Dockerfile

# Pull base image
FROM python:3.8

# Installs gettext utilities required to makemessages and compilemessages
RUN apt-get update && apt-get install -y --no-install-recommends \
	gettext \
	&& rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DJANGO_DEBUG=False
ENV DJANGO_DEBUG=$DJANGO_DEBUG

ARG DJANGO_ENV=production
ENV DJANGO_ENV=$DJANGO_ENV

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install 'pipenv==2018.11.26'
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system

# Copy project
COPY . /code/
