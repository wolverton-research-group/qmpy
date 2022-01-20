# Django settings for oqmd project.
import os
from dotenv import load_dotenv, find_dotenv

# Loading environment variables from .env file
load_dotenv(os.environ.get("QMPY_ENV_FILEPATH"))

INSTALL_PATH = os.path.dirname(os.path.abspath(__file__))
INSTALL_PATH = os.path.split(INSTALL_PATH)[0]
INSTALL_PATH = os.path.split(INSTALL_PATH)[0]

DEBUG = True if os.environ.get("OQMD_WEB_debug").lower() == "true" else False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ("Scott Kirklin", "scott.kirklin@gmail.com"),
    ("OQMD Dev Team", "oqmd.questions@gmail.com"),
)

MANAGERS = ADMINS

if not DEBUG:
    WSGI_APPLICATION = "qmpy.db.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("OQMD_DB_name"),
        "USER": os.environ.get("OQMD_DB_user"),
        "PASSWORD": os.environ.get("OQMD_DB_pswd"),
        "HOST": os.environ.get("OQMD_DB_host"),
        "PORT": os.environ.get("OQMD_DB_port"),
    }
}

ALLOWED_HOSTS = os.environ.get("OQMD_WEB_hosts").split(",")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "America/Chicago"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(INSTALL_PATH, "web", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.environ.get("OQMD_STATIC_root")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = os.environ.get("OQMD_STATIC_url")

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(INSTALL_PATH, "qmpy", "web", "static"),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("OQMD_DJANGO_secretkey")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(INSTALL_PATH, "qmpy", "web", "templates"),
        ],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                #'django.template.context_processors.tz',
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "libraries": {
                "staticfiles": "django.templatetags.static",
            },
        },
    },
]


MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "qmpy.web.urls"


INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "qmpy",
    "rest_framework",
    "rest_framework_xml",
    "rest_framework_yaml",
    "crispy_forms",
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}


REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKEND": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": "qmpy.utils.oqmd_optimade.IgnoreClientContentNegotiation",
    "PAGE_SIZE": 100,
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_xml.parsers.XMLParser",
        "rest_framework_yaml.parsers.YAMLParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_xml.renderers.XMLRenderer",
        "rest_framework_yaml.renderers.YAMLRenderer",
    ),
    "URL_FORMAT_OVERRIDE": "response_format",
    "FORMAT_SUFFIX_KWARG": "response_format",
}

CRIPSY_TEMPLATE_PACK = "bootstrap"

# CACHES = {
#        'default': {
#            'BACKEND':
#            'django.core.cache.backends.memcached.MemcachedCache',
#            'LOCATION': 'unix:/var/run/memcached/memcached.pid',
#            }
#        }

AUTH_USER_MODEL = "qmpy.User"

GOOGLE_ANALYTICS_MODEL = True
