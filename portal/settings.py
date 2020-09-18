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
import ast

import dj_database_url
from dotenv import load_dotenv
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from socket import gethostname, gethostbyname, gaierror

load_dotenv()

# Tests whether the second command line argument (after ./manage.py) was test
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, "VERSION")) as version_file:
    DJVERSION_VERSION = version_file.readline() or "0.0.0"

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
    gethostname(),
]

if not DEBUG and not TESTING:
    try:
        # this will fail locally because the macbook name can't be resolved to an IP
        host_by_name = gethostbyname(gethostname())
        ALLOWED_HOSTS.append(host_by_name)
    except gaierror:
        pass

if os.getenv("DJANGO_ALLOWED_HOSTS"):
    ALLOWED_HOSTS.extend(os.getenv("DJANGO_ALLOWED_HOSTS").split(","))

# Admins who get emailed about production errors
ADMINS = []

if os.getenv("DJANGO_ADMINS"):
    # DJANGO_ADMINS expects a tuple formatted as a string, eg '[("Paul", "paul@example.com"),("Bryan", "bryan@example.com")]'
    ADMINS.extend(ast.literal_eval(os.getenv("DJANGO_ADMINS")))

GITHUB_SHA = os.getenv("GITHUB_SHA") or None

# Application definition

INSTALLED_APPS = [
    "django_sass",
    "profiles",
    "covid_key",
    "invitations",
    "contact",
    "axes",
    "django.contrib.sites",  # Required for invitations
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",  # we want our auth templates loaded first
    "phonenumber_field",
    "django_otp",
    "otp_notify",
    "otp_yubikey",
    "easyaudit",
    "djversion",
    "widget_tweaks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "csp.middleware.CSPMiddleware",
    "easyaudit.middleware.easyaudit.EasyAuditMiddleware",
]

ROOT_URLCONF = "portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "portal", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portal.context_processors.logout_messages",
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

# database migrations will fail if env var is set to an empty string
if os.getenv("DATABASE_URL") == "":
    del os.environ["DATABASE_URL"]

if os.getenv("DATABASE_URL"):
    db_config = dj_database_url.config(
        default=os.getenv("DATABASE_URL"), conn_max_age=600, ssl_require=is_prod
    )
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
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {"user_attributes": ["name", "username"]},
    },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "profiles.validators.BannedPasswordValidator"},
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
CSRF_COOKIE_HTTPONLY = is_prod
SECURE_BROWSER_XSS_FILTER = is_prod

# Prefix session and csrf cookie names so they can not be over ridden by insecure hosts.
SESSION_COOKIE_NAME = "__secure-sessionid"
CSRF_COOKIE_NAME = "__secure-csrftoken"
# Limit session time to 1h of inactivity
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True

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
LOGOUT_REDIRECT_URL = "login"
OTP_NOTIFY_ENDPOINT = (
    os.getenv("OTP_NOTIFY_ENDPOINT") or "https://api.notification.alpha.canada.ca"
)
OTP_NOTIFY_API_KEY = os.getenv("OTP_NOTIFY_API_KEY")
OTP_NOTIFY_TEMPLATE_ID = os.getenv("OTP_NOTIFY_TEMPLATE_ID")
OTP_NOTIFY_TOKEN_VALIDITY = 90
OTP_EMAIL_THROTTLE_FACTOR = 3
# When DEBUG is on, we display the code directly in the form, no need to send it
if DEBUG:
    OTP_NOTIFY_NO_DELIVERY = True

API_AUTHORIZATION = os.getenv("API_AUTHORIZATION")
API_ENDPOINT = os.getenv("API_ENDPOINT")
DJANGO_EASY_AUDIT_READONLY_EVENTS = True
DJANGO_EASY_AUDIT_LOGGING_BACKEND = "portal.audit_backends.LoggerBackend"
DJANGO_EASY_AUDIT_UNREGISTERED_URLS_EXTRA = [r"^/status/"]
# If the header is set it must be available on the request or an Error will be thrown
if is_prod and not TESTING:
    DJANGO_EASY_AUDIT_REMOTE_ADDR_HEADER = "HTTP_X_FORWARDED_FOR"

CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_WHITELIST = []
CORS_ALLOW_METHODS = [
    "GET",
    "OPTIONS",
    "POST",
]

# This environment variable is automatically set for Heroku Review apps
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME") or False

# phonenumber_field app, default to Canadian numbers
PHONENUMBER_DEFAULT_REGION = "CA"

# Invitations app
SITE_ID = 1  # Required for invitations app
INVITATIONS_GONE_ON_ACCEPT_ERROR = False
INVITATIONS_SIGNUP_REDIRECT = "/signup/"
INVITATIONS_EMAIL_SUBJECT_PREFIX = ""
INVITATIONS_INVITATION_ONLY = True
INVITATIONS_INVITATION_EXPIRY = 1  # 1 day
INVITATIONS_ADMIN_ADD_FORM = "profiles.forms.HealthcareInvitationAdminAddForm"
INVITATIONS_ADMIN_CHANGE_FORM = "profiles.forms.HealthcareInvitationAdminChangeForm"
COVID_KEY_MAX_PER_USER = 200 if is_prod else 10000
COVID_KEY_MAX_PER_USER_PERIOD_SECONDS = 86400  # 1 day
MAX_INVITATIONS_PER_PERIOD = 25
MAX_INVITATIONS_PERIOD_SECONDS = 3540  # 59 minutes

# Email setup
EMAIL_BACKEND = (
    os.getenv("EMAIL_BACKEND") or "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT") or 587)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
email_use_tls = os.getenv("EMAIL_USE_TLS", "True")
EMAIL_USE_TLS = True if email_use_tls == "True" else False
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Create default Super User with this password
SU_DEFAULT_PASSWORD = os.getenv("SU_DEFAULT_PASSWORD", None)

# Login Rate Limiting
if TESTING:
    AXES_ENABLED = False
    AXES_VERBOSE = False
    OTP_NOTIFY_NO_DELIVERY = True

AXES_FAILURE_LIMIT = 10  # Lockout after 10 failed login attempts
AXES_SLOW_FAILURE_LIMIT = (
    100  # Second level of throttling to prevent slow attacks, 100 tries for 30 days
)
AXES_SLOW_FAILURE_COOLOFF_TIME = 30  # in days, second level of throttling

AXES_COOLOFF_MESSAGE = _(
    "This account has been locked due to too many failed log in attempts."
)
AXES_LOCKOUT_TEMPLATE = "locked_out.html"
AXES_COOLOFF_TIME = timedelta(hours=24)  # Lock out for 24 hours
AXES_ONLY_USER_FAILURES = True  # Default is to lockout both IP and username. We set this to True so it'll only lockout the username and not lockout a whole department behind a NAT
AXES_META_PRECEDENCE_ORDER = [  # Use the IP provided by the load balancer
    "HTTP_X_FORWARDED_FOR",
    "HTTP_X_REAL_IP",
    "REMOTE_ADDR",
]
AXES_HANDLER = "profiles.login_handler.HealthcareLoginHandler"
# Site Setup for Separate Domains

URL_DUAL_DOMAINS = os.getenv("URL_DUAL_DOMAINS", "False") == "True"

URL_EN_PRODUCTION = os.getenv(
    "URL_EN_PRODUCTION", "https://covid-alert-portal.alpha.canada.ca"
)
URL_FR_PRODUCTION = os.getenv(
    "URL_FR_PRODUCTION", "https://portail-alerte-covid.alpha.canada.ca"
)

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
]
CSP_CONNECT_SRC = ["'self'"]

FRESHDESK_API_ENDPOINT = os.getenv("FRESHDESK_API_ENDPOINT")
FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_PRODUCT_ID = int(os.getenv("FRESHDESK_PRODUCT_ID", 0)) or None

if TESTING:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {"null": {"class": "logging.NullHandler"}},
        "root": {"handlers": ["null"], "level": "CRITICAL"},
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "root": {"handlers": ["console"], "level": "INFO"},
    }
