from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#1y=b-#*=zkkgyeqn()j7g)-mdupps4$o)n9^tk9ij0qee@^tk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '1over3collective@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = '1OVER3 Store <1over3collective@gmail.com>'

MANAGERS = (
    ('Agbana Bolutife', 'agbanabolu@gmail.com'),
)

ADMINS = MANAGERS

CART_SESSION_ID = 'cart'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party

    # My APPS
    'accounts', 'store',
]

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = '/login/'

# Paystack
PAYSTACK_SECRET_KEY = Paystack(secret_key="sk_test_3bfa64c4c068e36a02f1625dc78f3551a149e627")
PAYSTACK_PUB_KEY = "pk_test_c88e3b49214ea1cfec35bdbff8ffc78829c6ca70"


CORS_REPLACE_HTTPS_REFERER      = True
HOST_SCHEME                     = "https://"
SECURE_PROXY_SSL_HEADER         = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT             = True
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True
SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
SECURE_HSTS_SECONDS             = 1000000
SECURE_FRAME_DENY               = True

