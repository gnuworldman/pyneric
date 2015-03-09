# -*- coding: utf-8 -*-
"""Django settings for an app used to test portions of the pyneric project."""

SECRET_KEY = 'j!9uth8@0x^_+%85=6ejv(3)9b=rqayvh@-_!_@regyoh_x*g)'

DEBUG = True

INSTALLED_APPS = (
    'django_test_app',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pyneric_test',
        'HOST': '',
        'PORT': '',
        'USER': 'postgres',
        'PASSWORD': '',
    }
}

try:
    from .settings_local import *
except ImportError:
    pass
