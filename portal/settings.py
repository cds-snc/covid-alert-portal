"""
Django settings for portal project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys
import dj_database_url

from dotenv import load_dotenv
from datetime import timedelta
from logging import getLogger, CRITICAL
from django.utils.translation import gettext_lazy as _

load_dotenv()

# Tests whether the second command line argument (after ./manage.py) was test
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    os.getenv("DJANGO_SECRET_KEY")
    or "j$e+wzxdum=!k$bwxpgt!$(@6!iasecid^tqnijx@r@o-6x%6d"
)

# Application security: should be set to True in production
# https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/#https
is_prod = os.getenv("DJANGO_ENV", "development") == "production"

# DEBUG will be True in a developemnt environment and false in production
DEBUG = not is_prod

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
    "localhost",
]

if os.getenv("ALLOWED_HOSTS"):
    ALLOWED_HOSTS.extend(os.getenv("ALLOWED_HOSTS").split(","))

# Application definition

INSTALLED_APPS = [
    "django_sass",
    "profiles",
    "invitations",
    "axes",
    "django.contrib.sites",  # Required for invitations
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",  # we want our auth templates loaded first
    "django_otp",
    "django_otp.plugins.otp_email",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",  # Needs to be first
    "django.contrib.auth.backends.ModelBackend",
]

WSGI_APPLICATION = "portal.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

default_db_path = os.path.join(BASE_DIR, "db.sqlite3")
if os.getenv("DATABASE_URL") == "":
    del os.environ["DATABASE_URL"]

if os.getenv("DATABASE_HOST") and not (os.getenv("DATABASE_HOST") == ""):
    db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "covid_portal",
        "USER": os.getenv("DATABASE_USERNAME"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST", "localhost"),
        "PORT": os.getenv("DATABASE_PORT", ""),
    }
else:
    db_config = dj_database_url.config(
        default=f"sqlite:///{default_db_path}", conn_max_age=600, ssl_require=is_prod
    )

DATABASES = {"default": db_config}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGES = (
    ("en", "English"),
    ("fr", "French"),
)

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SERVICE_NAME = "COVID Alert Portal"

SECURE_SSL_REDIRECT = is_prod
SESSION_COOKIE_SECURE = is_prod
CSRF_COOKIE_SECURE = is_prod
CSRF_COOKIE_HTTPONLY = is_prod
SECURE_BROWSER_XSS_FILTER = is_prod

# Prefix session and csrf cookie names so they can not be over ridden by insecure hosts.
SESSION_COOKIE_NAME = "__secure-sessionid"
CSRF_COOKIE_NAME = "__secure-csrftoken"
# Limit session times to 20h, this should make it that users need to relogin every morning.
SESSION_COOKIE_AGE = 72000

# Setting SECURE_SSL_REDIRECT on heroku was causing infinite redirects without this
if is_prod:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# For sites that should only be accessed over HTTPS, instruct modern browsers to refuse to connect to your domain name via an insecure connection (for a given period of time)
if is_prod:
    SECURE_HSTS_SECONDS = 31536000

# Instructs the browser to send a full URL, but only for same-origin links. No referrer will be sent for cross-origin links.
SECURE_REFERRER_POLICY = "same-origin"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

AUTH_USER_MODEL = "profiles.HealthcareUser"

LOGIN_URL = "login"
OTP_LOGIN_URL = "login-2fa"
LOGIN_REDIRECT_URL = "start"
LOGOUT_REDIRECT_URL = "landing"


# Invitations app
SITE_ID = 1  # Required for invitations app
INVITATIONS_GONE_ON_ACCEPT_ERROR = False
INVITATIONS_SIGNUP_REDIRECT = "/signup/"
INVITATIONS_EMAIL_SUBJECT_PREFIX = ""
INVITATIONS_INVITATION_ONLY = True

# Email setup
EMAIL_BACKEND = (
    os.getenv("EMAIL_BACKEND") or "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
email_use_tls = os.getenv("EMAIL_USE_TLS", "True")
EMAIL_USE_TLS = True if email_use_tls == "True" else False
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
OTP_EMAIL_SUBJECT = "Your login code"

# Default Super User Setup
CREATE_DEFAULT_SU = os.getenv("DJANGO_DEFAULT_SU", "False") == "True"
SU_DEFAULT_PASSWORD = os.getenv("SU_DEFAULT_PASSWORD", None)

# Login Rate Limiting
if TESTING:
    AXES_ENABLED = False
    AXES_VERBOSE = False
    AXES_LOGGER = "axes.watch_login"
    logger = getLogger(AXES_LOGGER)
    logger.setLevel(CRITICAL)

AXES_FAILURE_LIMIT = 5  # Lockout after 5 failed login attempts
AXES_COOLOFF_MESSAGE = _(
    "This account has been locked due to too many failed log in attempts. Please try again after 5 minutes."
)
AXES_LOCKOUT_TEMPLATE = "locked_out.html"
AXES_COOLOFF_TIME = timedelta(minutes=5)  # Lock out for 5 Minutes
AXES_ONLY_USER_FAILURES = True  # Default is to lockout both IP and username. We set this to True so it'll only lockout the username and not lockout a whole department behind a NAT
AXES_META_PRECEDENCE_ORDER = [  # Use the IP provided by the load balancer
    "HTTP_X_FORWARDED_FOR",
    "REAL_IP",
    "REMOTE_ADDR",
]

# HTTP Security headers configuration
# "js-agent.newrelic.com", "bam.nr-data.net" and "unsafe-inline" are required by New Relic:
# https://docs.newrelic.com/docs/browser/new-relic-browser/getting-started/compatibility-requirements-new-relic-browser#csp

CSP_DEFAULT_SRC = [
    "'self'",
    "staging.covid-hcportal.cdssandbox.xyz",
    "covid-alert-portal.alpha.canada.ca",
    "portail-alerte-covid.alpha.canada.ca",
]
CSP_STYLE_SRC = ["'self'", "fonts.googleapis.com"]
CSP_FONT_SRC = ["'self'", "fonts.gstatic.com"]
CSP_SCRIPT_SRC = [
    "'self'",
    "cdnjs.cloudflare.com",
    "js-agent.newrelic.com",
    "bam.nr-data.net",
]
CSP_CONNECT_SRC = ["'self'", "bam.nr-data.net"]
