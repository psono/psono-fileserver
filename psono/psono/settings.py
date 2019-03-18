"""
Django settings for psono project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import socket
import os
import yaml
import json
import binascii
import six
import uuid
from corsheaders.defaults import default_headers

import nacl.encoding
import nacl.signing
import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, PublicKey, Box
from django.conf import global_settings
from google.oauth2 import service_account

HOME = os.path.expanduser('~')

with open(os.path.join(HOME, '.psono_fileserver', 'settings.yaml'), 'r') as stream:
    config = yaml.safe_load(stream)


def config_get(key, *args):
    if 'PSONOFS_' + key in os.environ:
        val = os.environ.get('PSONOFS_' + key)
        try:
            json_object = json.loads(val)
        except ValueError:
            return val
        return json_object
    if key in config:
        return config.get(key)
    if len(args) > 0:
        return args[0]
    raise Exception("Setting missing", "Couldn't find the setting for %s (maybe you forgot the 'PSONOFS_' prefix in the environment variable" % (key,))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config_get('SECRET_KEY')
PRIVATE_KEY  = config_get('PRIVATE_KEY', '')
PUBLIC_KEY  = config_get('PUBLIC_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = config_get('ALLOWED_HOSTS')

READ = config_get('READ', True)
WRITE = config_get('WRITE', True)
DELETE = config_get('DELETE', True)
IP_READ_WHITELIST = config_get('IP_READ_WHITELIST', [])
IP_WRITE_WHITELIST = config_get('IP_WRITE_WHITELIST', [])
IP_READ_BLACKLIST = config_get('IP_READ_BLACKLIST', [])
IP_WRITE_BLACKLIST = config_get('IP_WRITE_BLACKLIST', [])

CLUSTER_ID = config_get('CLUSTER_ID')
CLUSTER_PRIVATE_KEY = config_get('CLUSTER_PRIVATE_KEY')

SHARDS_PUBLIC = []
SHARDS_DICT = {}

for s in config_get('SHARDS'):
    SHARDS_DICT[s['shard_id']] = s
    if SHARDS_DICT[s['shard_id']]['engine']['class'] == 'google_cloud' and 'credentials' in SHARDS_DICT[s['shard_id']]['engine']['kwargs']:
        SHARDS_DICT[s['shard_id']]['engine']['kwargs']['credentials'] = service_account.Credentials.from_service_account_file(
            SHARDS_DICT[s['shard_id']]['engine']['kwargs']['credentials']
        )

    SHARDS_PUBLIC.append({
        'shard_id': s['shard_id'],
        'read': s['read'] and READ,
        'write': s['write'] and WRITE,
        'delete': s['delete'] and DELETE
    })

HOST_URL = config_get('HOST_URL')
SERVER_URL = config_get('SERVER_URL')
SERVER_PUBLIC_KEY = config_get('SERVER_PUBLIC_KEY')
SERVER_URL_VERIFY_SSL = config_get('SERVER_URL_VERIFY_SSL', True)

FILESERVER_ID = str(uuid.uuid4())
FILESERVER_SESSION_KEY = nacl.encoding.HexEncoder.encode(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)).decode()

FILE_UPLOAD_MAX_MEMORY_SIZE = config_get('FILE_UPLOAD_MAX_MEMORY_SIZE', global_settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
DATA_UPLOAD_MAX_MEMORY_SIZE = config_get('DATA_UPLOAD_MAX_MEMORY_SIZE', global_settings.DATA_UPLOAD_MAX_MEMORY_SIZE)
FILE_UPLOAD_TEMP_DIR = config_get('FILE_UPLOAD_TEMP_DIR', global_settings.FILE_UPLOAD_TEMP_DIR)

AVAILABLE_FILESYSTEMS = {
    'local': 'django.core.files.storage.FileSystemStorage',
    'amazon_s3': 'storages.backends.s3boto3.S3Boto3Storage',
    'digital_ocean': 'storages.backends.s3boto3.S3Boto3Storage',
    'azure': 'storages.backends.azure_storage.AzureStorage',
    'dropbox': 'storages.backends.dropbox.DropBoxStorage',
    'google_cloud': 'storages.backends.gcloud.GoogleCloudStorage',
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'rest_framework',
    'restapi',
    'cron'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher'
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'restapi.parsers.DecryptJSONParser',
        # 'rest_framework.parsers.FormParser', # default for Form Parsing
        'rest_framework.parsers.MultiPartParser', # default for UnitTest Parsing
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'restapi.renderers.EncryptJSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1440/day',
        'user': '28800/day',
        'health_check': '61/hour',
        'cron': '61/minute',
        'transfer': '61/minute'
    },
}

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'restapi_query_formatter': {
#             '()': 'restapi.log.QueryFormatter',
#             'format': '%(time_utc)s logger=%(name)s, %(message)s'
#         }
#     },
#     'filters': {
#         'restapi_query_console': {
#             '()': 'restapi.log.FilterQueryConsole',
#         },
#     },
#     'handlers': {
#         'restapi_query_handler_console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'restapi_query_formatter',
#             'filters': ['restapi_query_console'],
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['restapi_query_handler_console'],
#         }
#     }
# }


for key, value in config_get('DEFAULT_THROTTLE_RATES', {}).items():
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'][key] = value # type: ignore

ROOT_URLCONF = 'psono.urls'
SITE_ID = 1

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = (
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
    )

CORS_ALLOW_HEADERS = default_headers + (
    'authorization-validator',
    'pragma',
    'if-modified-since',
    'cache-control',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'psono.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
  }
}

CACHE_ENABLE = config_get('CACHE_ENABLE', False)

if config_get('CACHE_DB', False):
    CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.db.DatabaseCache',
            "LOCATION": 'restapi_cache',
        }
    }

if config_get('CACHE_REDIS', False):
    CACHES = {
       "default": { # type: ignore
           "BACKEND": "django_redis.cache.RedisCache",
           "LOCATION": config_get('CACHE_REDIS_LOCATION', 'redis://localhost:6379/0'),
           "OPTIONS": {
               "CLIENT_CLASS": "django_redis.client.DefaultClient",
           }
       }
    }

if not config_get('THROTTLING', True):
    CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.dummy.DummyCache',
        }
    }

TIME_SERVER = config_get('TIME_SERVER', 'time.google.com')


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

with open(os.path.join(BASE_DIR, 'VERSION.txt')) as f:
    VERSION = f.readline().rstrip()

HOSTNAME = socket.getfqdn()

SESSION_CRYPTO_BOX = nacl.secret.SecretBox(FILESERVER_SESSION_KEY, encoder=nacl.encoding.HexEncoder)

def generate_fileserver_info():
    cluster_crypto_box = Box(PrivateKey(CLUSTER_PRIVATE_KEY, encoder=nacl.encoding.HexEncoder),
                             PublicKey(SERVER_PUBLIC_KEY, encoder=nacl.encoding.HexEncoder))

    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    encrypted = cluster_crypto_box.encrypt(json.dumps({
        'VERSION': VERSION,
        'hostname': HOSTNAME,
        'CLUSTER_ID': CLUSTER_ID,
        'FILESERVER_ID': FILESERVER_ID,
        'FILESERVER_PUBLIC_KEY': PUBLIC_KEY,
        'FILESERVER_SESSION_KEY': FILESERVER_SESSION_KEY,
        'SHARDS_PUBLIC': SHARDS_PUBLIC,
        'READ': READ,
        'WRITE': WRITE,
        'DELETE': DELETE,
        'IP_READ_WHITELIST': IP_READ_WHITELIST,
        'IP_WRITE_WHITELIST': IP_WRITE_WHITELIST,
        'IP_READ_BLACKLIST': IP_READ_BLACKLIST,
        'IP_WRITE_BLACKLIST': IP_WRITE_BLACKLIST,
        'HOST_URL': HOST_URL,
    }).encode("utf-8"), nonce)

    return nacl.encoding.HexEncoder.encode(encrypted).decode()

FILESERVER_INFO = generate_fileserver_info()

def generate_signature():

    info = {
        'version': VERSION,
        'hostname': HOSTNAME,
        'fileserver_id': FILESERVER_ID,
        'api': 1,
        'public_key': PUBLIC_KEY,
        'cluster_id': CLUSTER_ID,
        'shards': SHARDS_PUBLIC,
        'read': READ,
        'write': WRITE,
        'delete': DELETE,
        'host_url': HOST_URL,
    }

    info = json.dumps(info)

    signing_box = nacl.signing.SigningKey(PRIVATE_KEY, encoder=nacl.encoding.HexEncoder)
    verify_key = signing_box.verify_key.encode(encoder=nacl.encoding.HexEncoder)
    # The first 128 chars (512 bits or 64 bytes) are the actual signature, the rest the binary encoded info
    signature = binascii.hexlify(signing_box.sign(six.b(info)))[:128]

    return {
        'info': info,
        'signature': signature,
        'verify_key': verify_key,
    }

SIGNATURE = generate_signature()
