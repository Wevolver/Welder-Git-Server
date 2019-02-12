import os
import json
import sys
import warnings
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = default_headers + ('Permissions', )
CORS_EXPOSE_HEADERS = [
    'Permissions',
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'ggec94x-e8!9pfqz2(ev32gxpq#w)81v4wa@cuc3tur77$s!1a'

DEBUG = True

ALLOWED_HOSTS = [
    '69e77e5c.ngrok.io', '5a77b1ab.ngrok.io', 'www.wevolver.com',
    'test.wevolver.com', 'git.wevolver.com', 'dev.wevolver.com',
    'welder.wevolver.com', 'localhost', '127.0.0.1', 'welder'
]

DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000

INSTALLED_APPS = (
    'robots',
    'corsheaders',
    'django.contrib.sites',
    'django.contrib.contenttypes',
)

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

X_FRAME_OPTIONS = 'ALLOW-FROM https://www.wevolver.com/'
ROOT_URLCONF = 'welder.urls'
WSGI_APPLICATION = 'welder.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

if not os.path.exists('logs/'):
    os.makedirs('logs/')

with open(os.path.join('logs', 'main_debug.log'), 'w'):
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format':
            '%(asctime)s %(levelname)-8s [%(name)s:%(lineno)s] %(message)s',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

if os.environ.get('TRAVIS') == 'true':
    API_BASE = 'https://dev.wevolver.com'
    AUTH_BASE = 'https://dev.wevolver.com/o'
    API_V2_BASE = 'https://dev.wevolver.com/api/v2'
    TOKEN_SECRET = 'TOKEN_SECRET'
    REPO_DIRECTORY = './'
    TRACKING_TOKEN = "TRACKING_TOKEN"
else:
    try:
        with open("env.json") as f:
            environment = json.loads(f.read())
    except:
        with open("../env.json") as f:
            environment = json.loads(f.read())

    def get_env(setting, env=environment):
        """Get the env variable or return explicit exception."""
        try:
            return env[setting]
        except KeyError:
            print("No key: " + setting)
            sys.exit(0)
            return False

    API_BASE = get_env("API_BASE")
    AUTH_BASE = get_env("AUTH_BASE")
    API_V2_BASE = get_env("API_V2_BASE")
    TOKEN_SECRET = get_env("TOKEN_SECRET")
    REPO_DIRECTORY = get_env("REPO_DIRECTORY")
    TRACKING_TOKEN = get_env("TRACKING_TOKEN")
    AWS_ACCESS_KEY_ID = get_env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = get_env("AWS_SECRET_ACCESS_KEY")

try:
    from welder.settings_local import *
except ImportError:
    warnings.warn('No local settings found', RuntimeWarning)
