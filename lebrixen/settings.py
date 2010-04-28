#encoding=UTF-8
import os
import logging
#import socket
# Django settings for lebrixen project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET = 'utf-8'
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
ADMINS = (
     ('Luis Borjas', 'luis.borjas@escolarea.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'lebrixen'             # Or path to database file if using sqlite3.
DATABASE_USER = 'lebrixen'             # Not used with sqlite3.
DATABASE_PASSWORD = '1f0581d8c9709208def8a96b5a960de4'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Tegucigalpa'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

#LANGUAGES=(
#           ('en', u'English'),
#           ('es', u'Español'),
#           ('fr', u'Français'),
#           )


# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n@iv5^hueu9hzmyux0(3x--+!mz%9@hj8j7!s5xx&a*#lack)i'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'lebrixen.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_PATH, 'templates')
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'celery', 
    'djapian',   
    'search',
    'service',		
    #'profile',
)

#settings for celery:
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "lebrixen"
BROKER_PASSWORD = "a5c622e9a8d91d165b37710627946720"
BROKER_VHOST = "lebrixen_broker"

STATIC_DOC_ROOT = os.path.join(ROOT_PATH, 'static')

#keys for web services:
WEB_SERVICES_KEYS = {
    'wordsfinder' : 'c34f27a46cd4464528ffacdf24e350c5',
    'alchemy': '622775ee9f8813c72e44522f4dcdd11c8da53ee1',
    'yahoo': 'w90Ugc3V34GwIC1p4HZcO53uQJ2YNWDjjLMvpLxa34ewJYbsuhkY4.VSOrh_APM-',
    'opencalais': 'vnccvbw7z4bm4845qcztrtyr',
    'extractor':  'e840cbe5-2d29-4ab2-b6a9-18746a61c125',
}

#set up the logging facility:
if DEBUG:
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
    )
else:
    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s %(levelname)s %(message)s',
        filename = '/tmp/lebrixen.log',
        filemode = 'w'
    )

#settings for djapian:
DJAPIAN_DATABASE_PATH = os.path.join(ROOT_PATH, 'djapian_spaces')

#how much time to wait before the index is rebuilt (in seconds)
UPDATE_INDEX_INTERVAL = 10*60

#cf: http://code.google.com/p/djapian/wiki/Stemming
DJAPIAN_STEMMING_LANG = "multi"

try:
    from local_settings import *
except:
    pass

