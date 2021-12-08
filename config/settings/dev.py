import os

from decouple import Csv, config

from .base import *

DEBUG = config('DEBUG', default=1, cast=lambda x: int(x))

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': config(
            'SQL_ENGINE',
            default='django.db.backends.sqlite3'
        ),
        'NAME': config(
            'SQL_DATABASE',
            default=os.path.join(BASE_DIR, 'db.sqlite3')
        ),
        'USER': config('SQL_USER', default='user'),
        'PASSWORD': config('SQL_PASSWORD', default='password'),
        'HOST': config('SQL_HOST', default='localhost'),
        'PORT': config('SQL_PORT', default='5432'),
    }
}
