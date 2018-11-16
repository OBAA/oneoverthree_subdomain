from django.core.exceptions import ImproperlyConfigured
import datetime
import json
import os

with open(os.path.abspath("secrets.json")) as f:
    secrets = json.loads(f.read())


def get_secret_setting(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured("Set the {} setting".format(setting))


AWS_GROUP_NAME = get_secret_setting('AWS_GROUP_NAME')
AWS_USERNAME = get_secret_setting('AWS_USERNAME')
AWS_ACCESS_KEY_ID = get_secret_setting('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_secret_setting('AWS_SECRET_ACCESS_KEY')

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'oneoverthree.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'oneoverthree.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = get_secret_setting('AWS_STORAGE_BUCKET_NAME')
S3DIRECT_REGION = get_secret_setting('S3DIRECT_REGION')
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

