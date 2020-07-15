"""
WSGI config for portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import newrelic.agent

newrelic.agent.initialize("./newrelic.ini")

# The following errors are ignored in order for New Relic Agent to initialize first.
import os  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

# Uses the following env vars to set config
# NEW_RELIC_LICENSE_KEY
# NEW_RELIC_APP_NAME

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portal.settings")

application = get_wsgi_application()
