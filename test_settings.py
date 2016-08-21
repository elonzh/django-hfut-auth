# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

SECRET_KEY = 'psst'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_hfut'
)

# https://docs.djangoproject.com/en/dev/ref/databases/#database-is-locked-errors
# https://docs.djangoproject.com/en/dev/ref/settings/#engine
# http://stackoverflow.com/questions/37216731/postgresql-in-memory-database-django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_hfut',
        'USER': 'postgres',
        'PASSWORD': 'sql&admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_hfut.backends.HFUTBackend'
)

# default
DJANGO_HFUT_CAMPUS = 'ALL'
