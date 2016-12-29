from .common import *

SECRET_KEY = '0vb+-_-52phz@ii^cxr+mlgvmn6fctd+v5qpnv&k+-00#u-==0'

DEBUG = True

ALLOWED_HOSTS = []

WSGI_APPLICATION = 'web.wsgi.local.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tomo',
        'USER': 'tomo',
        'PASSWORD': 'tomo',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'
SUBMISSION_URL = 'http://127.0.0.1:8000'

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# Tell nose to measure coverage on the 'problems', 'attemtps', 'courses' and 'users' apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=problems,attempts,courses,users,utils',
]
