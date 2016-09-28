# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import json

from django.core.exceptions import ImproperlyConfigured
from .base import *

from unipath import Path


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
INSTALLED_APPS += ('debug_toolbar',)

BASE_DIR = Path(__file__).absolute().ancestor(3)
SECRETS_FILE = os.path.join(BASE_DIR.ancestor(1), 'config.json')

with open(SECRETS_FILE) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("SECRET_KEY")

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pdl',
        'USER': get_secret("DB_USER"),
        'PASSWORD': get_secret("DB_PASS"),
        'HOST': 'localhost',
        'PORT': get_secret('DB_PORT'),
    }
}

# optional for scrapper
CRAWLERA_USER = get_secret("CRAWLERA_USER")
CRAWLERA_PASS = get_secret("CRAWLERA_PASS")

TESTING = False
