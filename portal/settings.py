"""
Django settings for portal project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import dj_database_url

from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

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
    "whitenoise.runserver_nostatic",
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
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
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


SECURE_SSL_REDIRECT = is_prod
SESSION_COOKIE_SECURE = is_prod
CSRF_COOKIE_SECURE = is_prod
SECURE_BROWSER_XSS_FILTER = is_prod

# Setting SECURE_SSL_REDIRECT on heroku was causing infinite redirects without this
if is_prod:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# For sites that should only be accessed over HTTPS, instruct modern browsers to refuse to connect to your domain name via an insecure connection (for a given period of time)
SECURE_HSTS_SECONDS = 3600 if is_prod else 0

# Instructs the browser to send a full URL, but only for same-origin links. No referrer will be sent for cross-origin links.
SECURE_REFERRER_POLICY = "same-origin"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

AUTH_USER_MODEL = "profiles.HealthcareUser"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "start"
LOGOUT_REDIRECT_URL = "landing"


# Invitations app
SITE_ID = 1  # Required for invitations app
INVITATIONS_GONE_ON_ACCEPT_ERROR = False
INVITATIONS_SIGNUP_REDIRECT = "/signup/"
INVITATIONS_EMAIL_SUBJECT_PREFIX = ""
INVITATIONS_INVITATION_ONLY = True

# Email setup
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
email_use_tls = os.getenv("EMAIL_USE_TLS", "True")
EMAIL_USE_TLS = True if email_use_tls == "True" else False
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Default Super User Setup
CREATE_DEFAULT_SU = os.getenv("DJANGO_DEFAULT_SU", "False") == "True"
SU_DEFAULT_PASSWORD = os.getenv("SU_DEFAULT_PASSWORD", None)

# Login Rate Limiting
if os.getenv("DJANGO_ENV", "production") == "tests":
    AXES_ENABLED = False

AXES_FAILURE_LIMIT = 10  # Lockout after 10 failed login attempts
AXES_ONLY_USER_FAILURES = False  # Default is to lockout both IP and username. If we set this to True it'll only lockout the username
AXES_COOLOFF_TIME = timedelta(minutes=5)  # Lock out for 5 Minutes
AXES_META_PRECEDENCE_ORDER = [  # Use the IP provided by the load balancer
    "HTTP_X_FORWARDED_FOR",
    "REAL_IP",
    "REMOTE_ADDR",
]
