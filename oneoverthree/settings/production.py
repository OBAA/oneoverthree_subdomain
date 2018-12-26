from .base import *

# AWS S3
from oneoverthree.aws.conf import *

import json
from django.core.exceptions import ImproperlyConfigured

with open(os.path.abspath("secrets.json")) as f:
    secrets = json.loads(f.read())


def get_secret_setting(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured("Set the {} setting".format(setting))


# Site Identification
SITE_ID = 1

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_setting('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.1over3.store', '46.101.17.31']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'mptt', 'storages', 'dbbackup',

    # My APPS
    'accounts', 'addresses',
    'analytics', 'billing',  # 'blog',
    'cart', 'dashboard',
    'filter', 'marketplace',
    'marketing', 'orders',
    'store', 'search', 'tags',
]

AUTH_USER_MODEL = 'accounts.User'

BASE_URL = 'www.1over3.store'

CART_SESSION_ID = 'cart'

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/home/oneoverthree/oneoverthree_subdomain/backups'}

DEFAULT_SITE_DOMAIN = 'www.1over3.store'

DEFAULT_FROM_EMAIL = get_secret_setting('DEFAULT_FROM_EMAIL')

EMAIL_HOST = get_secret_setting('EMAIL_HOST')
EMAIL_HOST_USER = get_secret_setting('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret_setting('EMAIL_HOST_PASSWORD')
EMAIL_PORT = get_secret_setting('EMAIL_PORT')
EMAIL_USE_TLS = True


MANAGERS = (
    ('Agbana Kunle', get_secret_setting('MANAGER1_EMAIL')),
)

ADMINS = MANAGERS

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = '/login/'

# MAILCHIMP
MAILCHIMP_API_KEY = get_secret_setting('MAILCHIMP_API_KEY')
MAILCHIMP_DATA_CENTER = get_secret_setting('MAILCHIMP_DATA_CENTER')
MAILCHIMP_EMAIL_LIST_ID = get_secret_setting('MAILCHIMP_EMAIL_LIST_ID')

# Paystack Test
PAYSTACK_SECRET_TEST_KEY = Paystack(secret_key=get_secret_setting('PAYSTACK_SECRET_KEY'))
PAYSTACK_PUB_TEST_KEY = "pk_test_c88e3b49214ea1cfec35bdbff8ffc78829c6ca70"

# Paystack Live
PAYSTACK_SECRET_LIVE_KEY = Paystack(secret_key=get_secret_setting('PAYSTACK_SECRET_KEY'))
PAYSTACK_PUB_LIVE_KEY = "pk_live_e6c6c77fa7e3b6d3bc40ff7081334197218b7166"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret_setting('DATABASE_NAME'),
        'USER': get_secret_setting('DATABASE_USER'),
        'PASSWORD': get_secret_setting('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

CORS_REPLACE_HTTPS_REFERER      = True
HOST_SCHEME                     = "https://"
SECURE_PROXY_SSL_HEADER         = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT             = True
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True
SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
SECURE_HSTS_SECONDS             = 1000000
SECURE_FRAME_DENY               = True

