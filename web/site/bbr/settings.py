# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

"""
Django settings for bbr4 project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
from bbr.settings_common import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f69cytx1o42nne1tm1@b$v0$9yl)0!+iqo+yjpsh!tq6abnuw_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

GOOGLE_MAPS_API_KEY = "AIzaSyDRGGo0pfBGKEE5n6iS7IEqhWeSHYiEI2c"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bbr3',
        'USER': 'bbr',
        'PASSWORD':'2barsrepeat',
        'HOST':'sokar',
        'PORT':'5432',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/site_media/'
UPLOAD_URL = 'http://bbr-media-upload.s3-website.eu-west-2.amazonaws.com/'
THUMBS_URL = 'http://bbr-media-upload-thumbnail.s3-website.eu-west-2.amazonaws.com/'

AWS_REGION = 'eu-west-2'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "site_media"),
]

NOTIFICATIONS_ENABLED = False
NOTIFICATION_TOPIC_ARN = "ABC123"
