from .base import *
from .secrets import secrets

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secrets.get('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'mptt',

    # My APPS
    'accounts', 'addresses',
    'analytics', 'billing',  # 'blog',
    'cart', 'dashboard',
    'filter', 'marketplace',
    'marketing', 'orders',
    'store', 'search', 'tags',
]

AUTH_USER_MODEL = 'accounts.User'

CART_SESSION_ID = 'cart'

DEFAULT_SITE_DOMAIN = '127.0.0.1:8000'

DEFAULT_FROM_EMAIL = '1OVER3 Store <1over3collective@gmail.com>'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = secrets.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = secrets.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

MANAGERS = (
    ('OBAA', 'itsobaa@gmail.com'),
)

ADMINS = MANAGERS

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = '/login/'

# MAILCHIMP
MAILCHIMP_API_KEY = secrets.get('MAILCHIMP_API_KEY')
MAILCHIMP_DATA_CENTER = secrets.get('MAILCHIMP_DATA_CENTER')
MAILCHIMP_EMAIL_LIST_ID = secrets.get('MAILCHIMP_EMAIL_LIST_ID')

# Paystack
PAYSTACK_SECRET_KEY = Paystack(secret_key=secrets.get('PAYSTACK_SECRET_KEY'))
PAYSTACK_PUB_KEY = "pk_test_c88e3b49214ea1cfec35bdbff8ffc78829c6ca70"


CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = "http://"
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
CSRF_COOKIE_SECURE              = False
SECURE_HSTS_SECONDS             = None
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_FRAME_DENY               = False
