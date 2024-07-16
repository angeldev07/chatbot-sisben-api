from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'oqx(+js37!7(-5-b0ie+1k+_dl62p-kkp#9pzk0_nu=&0zbw6c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}