"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import sys
import warnings
from datetime import timedelta
from importlib import reload

import dj_database_url
from environs import Env
import requests
from corsheaders.defaults import default_headers
from django.core.management.utils import get_random_secret_key

env = Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ENV = env("ENVIRONMENT", default="local")
if ENV not in ("local", "dev", "staging", "production"):
    warnings.warn(
        "ENVIRONMENT env variable must be one of local, dev, staging or production"
    )

DEBUG = env("DEBUG", default=False)

SECRET_KEY = env("DJANGO_SECRET_KEY", default=get_random_secret_key())

HOSTED_SEATS_LIMIT = env.int("HOSTED_SEATS_LIMIT", default=0)

# Google Analytics Configuration
GOOGLE_ANALYTICS_KEY = env("GOOGLE_ANALYTICS_KEY", default="")
GOOGLE_SERVICE_ACCOUNT = env("GOOGLE_SERVICE_ACCOUNT", default=None)
if not GOOGLE_SERVICE_ACCOUNT:
    warnings.warn(
        "GOOGLE_SERVICE_ACCOUNT not configured, getting organisation usage will not work"
    )
GA_TABLE_ID = env("GA_TABLE_ID", default=None)
if not GA_TABLE_ID:
    warnings.warn(
        "GA_TABLE_ID not configured, getting organisation usage will not work"
    )

INFLUXDB_TOKEN = env.str("INFLUXDB_TOKEN", default="")
INFLUXDB_BUCKET = env.str("INFLUXDB_BUCKET", default="")
INFLUXDB_URL = env.str("INFLUXDB_URL", default="")
INFLUXDB_ORG = env.str("INFLUXDB_ORG", default="")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

INTERNAL_IPS = ["127.0.0.1"]

# In order to run a load balanced solution, we need to whitelist the internal ip
try:
    internal_ip = requests.get("http://instance-data/latest/meta-data/local-ipv4").text
except requests.exceptions.ConnectionError:
    pass
else:
    ALLOWED_HOSTS.append(internal_ip)
del requests

if sys.version[0] == "2":
    reload(sys)
    sys.setdefaultencoding("utf-8")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "django.contrib.sites",
    "custom_auth",
    "admin_sso",
    "api",
    "corsheaders",
    "users",
    "organisations",
    "projects",
    "sales_dashboard",
    "environments",
    "environments.permissions",
    "environments.identities",
    "environments.identities.traits",
    "features",
    "segments",
    "e2etests",
    "simple_history",
    "drf_yasg2",
    "audit",
    "permissions",
    "projects.tags",
    # 2FA
    "trench",
    # health check plugins
    "health_check",
    "health_check.db",
    # Used for ordering models (e.g. FeatureSegment)
    "ordered_model",
    # Third party integrations
    "integrations.datadog",
    "integrations.amplitude",
    "integrations.sentry",
    # Rate limiting admin endpoints
    "axes",
]

if GOOGLE_ANALYTICS_KEY or INFLUXDB_TOKEN:
    INSTALLED_APPS.append("analytics")

SITE_ID = 1

DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"), conn_max_age=60)}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "PAGE_SIZE": 10,
    "UNICODE_JSON": False,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_THROTTLE_RATES": {"login": "1/s"},
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

if GOOGLE_ANALYTICS_KEY:
    MIDDLEWARE.append("analytics.middleware.GoogleAnalyticsMiddleware")

if INFLUXDB_TOKEN:
    MIDDLEWARE.append("analytics.middleware.InfluxDBMiddleware")

ALLOWED_ADMIN_IP_ADDRESSES = env.list("ALLOWED_ADMIN_IP_ADDRESSES", default=list())
if len(ALLOWED_ADMIN_IP_ADDRESSES) > 0:
    warnings.warn(
        "Restricting access to the admin site for ip addresses %s"
        % ", ".join(ALLOWED_ADMIN_IP_ADDRESSES)
    )
    MIDDLEWARE.append("app.middleware.AdminWhitelistMiddleware")

ROOT_URLCONF = "app.urls"

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

WSGI_APPLICATION = "app.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "admin_sso.auth.DjangoSSOAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

DJANGO_ADMIN_SSO_OAUTH_CLIENT_ID = env.str("OAUTH_CLIENT_ID", default="")
DJANGO_ADMIN_SSO_OAUTH_CLIENT_SECRET = env.str("OAUTH_CLIENT_SECRET", default="")

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "../../static/")

# CORS settings

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = default_headers + ("X-Environment-Key", "X-E2E-Test-Auth-Token")

DEFAULT_FROM_EMAIL = env("SENDER_EMAIL", default="noreply@bullet-train.io")
EMAIL_CONFIGURATION = {
    # Invitations with name is anticipated to take two arguments. The persons name and the
    # organisation name they are invited to.
    "INVITE_SUBJECT_WITH_NAME": "%s has invited you to join the organisation '%s' on Bullet "
    "Train",
    # Invitations without a name is anticipated to take one arguments. The organisation name they
    # are invited to.
    "INVITE_SUBJECT_WITHOUT_NAME": "You have been invited to join the organisation '%s' on "
    "Bullet Train",
    # The email address invitations will be sent from.
    "INVITE_FROM_EMAIL": DEFAULT_FROM_EMAIL,
}

AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME", default=None)
AWS_SES_REGION_ENDPOINT = env("AWS_SES_REGION_ENDPOINT", default=None)

# Used on init to create admin user for the site, update accordingly before hitting /auth/init
ALLOW_ADMIN_INITIATION_VIA_URL = True
ADMIN_EMAIL = "admin@example.com"
ADMIN_INITIAL_PASSWORD = "password"

AUTH_USER_MODEL = "users.FFAdminUser"

ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"  # TODO: configure email verification

# SendGrid
EMAIL_BACKEND = env("EMAIL_BACKEND", default="sgbackend.SendGridBackend")
SENDGRID_API_KEY = env("SENDGRID_API_KEY", default=None)
if EMAIL_BACKEND == "sgbackend.SendGridBackend" and not SENDGRID_API_KEY:
    warnings.warn(
        "`SENDGRID_API_KEY` has not been configured. You will not receive emails."
    )

SWAGGER_SETTINGS = {
    "SHOW_REQUEST_HEADERS": True,
    "SECURITY_DEFINITIONS": {
        "api_key": {"type": "apiKey", "in": "header", "name": "Authorization"}
    },
}

LOGIN_URL = "/admin/login/"
LOGOUT_URL = "/admin/logout/"

# Email associated with user that is used by front end for end to end testing purposes
FE_E2E_TEST_USER_EMAIL = "nightwatch@solidstategroup.com"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Chargebee
ENABLE_CHARGEBEE = env.bool("ENABLE_CHARGEBEE", default=False)
CHARGEBEE_API_KEY = env("CHARGEBEE_API_KEY", default=None)
CHARGEBEE_SITE = env("CHARGEBEE_SITE", default=None)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_format": {"format": "%(name)-12s %(levelname)-8s %(message)s"}
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console_format",
        },
    },
    "loggers": {
        "django": {"level": "INFO", "handlers": ["console"]},
        "": {"level": "DEBUG", "handlers": ["console"]},
    },
}

CACHE_FLAGS_SECONDS = env.int("CACHE_FLAGS_SECONDS", default=0)
FLAGS_CACHE_LOCATION = "environment-flags"
ENVIRONMENT_CACHE_LOCATION = "environment-objects"

CACHE_PROJECT_SEGMENTS_SECONDS = env.int("CACHE_PROJECT_SEGMENTS_SECONDS", 0)
PROJECT_SEGMENTS_CACHE_LOCATION = "project-segments"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    },
    ENVIRONMENT_CACHE_LOCATION: {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": ENVIRONMENT_CACHE_LOCATION,
    },
    FLAGS_CACHE_LOCATION: {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": FLAGS_CACHE_LOCATION,
    },
    PROJECT_SEGMENTS_CACHE_LOCATION: {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": PROJECT_SEGMENTS_CACHE_LOCATION,
    },
}

LOG_LEVEL = env.str("LOG_LEVEL", default="WARNING")

TRENCH_AUTH = {
    "FROM_EMAIL": DEFAULT_FROM_EMAIL,
    "BACKUP_CODES_QUANTITY": 5,
    "BACKUP_CODES_LENGTH": 10,  # keep (quantity * length) under 200
    "BACKUP_CODES_CHARACTERS": (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    ),
    "DEFAULT_VALIDITY_PERIOD": 30,
    "CONFIRM_BACKUP_CODES_REGENERATION_WITH_CODE": True,
    "APPLICATION_ISSUER_NAME": "app.bullet-train.io",
    "MFA_METHODS": {
        "app": {
            "VERBOSE_NAME": "TOTP App",
            "VALIDITY_PERIOD": 60 * 10,
            "USES_THIRD_PARTY_CLIENT": True,
            "HANDLER": "custom_auth.mfa.backends.application.CustomApplicationBackend",
        },
    },
}

USER_CREATE_PERMISSIONS = env.list(
    "USER_CREATE_PERMISSIONS", default=["rest_framework.permissions.AllowAny"]
)

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password-reset/confirm/{uid}/{token}",
    # if True user required to click activation link in email to activate account
    "SEND_ACTIVATION_EMAIL": env.bool("ENABLE_EMAIL_ACTIVATION", default=False),
    "ACTIVATION_URL": "activate/{uid}/{token}",  # FE uri to redirect user to from activation email
    "SEND_CONFIRMATION_EMAIL": False,  # register or activation endpoint will send confirmation email to user
    "SERIALIZERS": {
        "token": "custom_auth.serializers.CustomTokenSerializer",
        "user_create": "custom_auth.serializers.CustomUserCreateSerializer",
        "current_user": "users.serializers.CustomCurrentUserSerializer",
    },
    "EMAIL": {
        "activation": "users.emails.ActivationEmail",
        "confirmation": "users.emails.ConfirmationEmail",
    },
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "HIDE_USERS": True,
    "PERMISSIONS": {
        "user": ["custom_auth.permissions.CurrentUser"],
        "user_list": ["custom_auth.permissions.CurrentUser"],
        "user_create": USER_CREATE_PERMISSIONS,
    },
}

# Github OAuth credentials
GITHUB_CLIENT_ID = env.str("GITHUB_CLIENT_ID", default="")
GITHUB_CLIENT_SECRET = env.str("GITHUB_CLIENT_SECRET", default="")

# Django Axes settings
ENABLE_AXES = env.bool("ENABLE_AXES", default=False)
if ENABLE_AXES:
    # must be the first item in the auth backends
    AUTHENTICATION_BACKENDS.insert(0, "axes.backends.AxesBackend")
    # must be the last item in the middleware stack
    MIDDLEWARE.append("app.middleware.AxesMiddleware")
    AXES_COOLOFF_TIME = timedelta(minutes=env.int("AXES_COOLOFF_TIME", 15))
    AXES_BLACKLISTED_URLS = [
        "/admin/login/?next=/admin",
        "/admin/",
    ]

# Sentry tracking
SENTRY_SDK_DSN = env("SENTRY_SDK_DSN", default=None)
SENTRY_TRACE_SAMPLE_RATE = env.float("SENTRY_TRACE_SAMPLE_RATE", default=1.0)
