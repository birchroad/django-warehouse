from os.path import dirname, join
import logging

TEST_ROOT = dirname(__file__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=join(TEST_ROOT, 'test.log'),
    filemode='w'
)

INSTALLED_APPS = ('warehouse', 'tests',
                  'django.contrib.sites',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': join(TEST_ROOT, 'db.sqlite'), # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

SITE_ID = 1

#MEDIA_URL = '/site_media/media/'
#MEDIA_ROOT = join(TEST_ROOT, 'project', 'site_media', 'media')



ROOT_URLCONF = 'tests.urls'

TEMPLATE_DIRS = (join(TEST_ROOT, 'templates'),)
