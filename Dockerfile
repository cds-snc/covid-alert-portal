# Dockerfile

# Pull base image
FROM python:3.8-slim

# Create a group and user to run our app
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

# Installs gettext utilities required to makemessages and compilemessages
RUN apt-get update && apt-get install -y --no-install-recommends \
	gettext \
		make \
		build-essential \
		mime-support \
		git \
	&& rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install 'pipenv==2018.11.26'
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system --deploy

# Copy project

COPY . /code/
# Change to a non-root user
RUN chmod +x ./entrypoint.sh
RUN chown -R ${APP_USER}:${APP_USER} /code/

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

CMD ./entrypoint.sh