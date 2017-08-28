import os
import json
from django.core.exceptions import ImproperlyConfigured
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = default_headers + (
    'Permissions',
)
CORS_EXPOSE_HEADERS = ['Permissions',]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'ggec94x-e8!9pfqz2(ev32gxpq#w)81v4wa@cuc3tur77$s!1a'

# DEBUG = False
DEBUG = True

ALLOWED_HOSTS = [ '*.wevolver.com', 'test.wevolver.com', 'dev.wevolver.com', 'welder.wevolver.com', 'localhost', '127.0.0.1', 'welder' ]

DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000

# Application definition

INSTALLED_APPS = (
    'robots',
    'corsheaders',
    'django.contrib.sites',
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    # 'django.contrib.staticfiles',
)

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'welder.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.loaders.app_directories.Loader',
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

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
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
        'format': '%(levelname)s:%(name)s: %(message)s '
        '(%(asctime)s; %(filename)s:%(lineno)d)',
        'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/main_debug.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_true'],
        },
        'null': {
            "class": 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
        'handlers': ['console'],
        'level': 'ERROR',
        'propagate': True,
        },
        'django': {
            'handlers': ['null', ],
        },
        'py.warnings': {
            'handlers': ['null', ],
        },
        '': {
        'handlers': ['console', 'debug_file'],
            'level': "DEBUG",
        },
    }
}


print(os.environ.get('TRAVIS') == 'true')
if os.environ.get('TRAVIS') == 'true':
    API_BASE = 'https://dev.wevolver.com'
    AUTH_BASE = 'https://dev.wevolver.com/o'
    TOKEN_SECRET = 'TOKEN_SECRET'
    REPO_DIRECTORY = './'

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
            error_msg = "Set the {0} environment variable".format(setting)
            raise ImproperlyConfigured(error_msg)

    API_BASE = get_env("API_BASE")
    AUTH_BASE = get_env("AUTH_BASE")
    TOKEN_SECRET = get_env("TOKEN_SECRET")
    REPO_DIRECTORY = get_env("REPO_DIRECTORY")
