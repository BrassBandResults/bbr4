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
SECRET_KEY = '${djangoSecretKey}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['bbr4.brassbandresults.co.uk',]

GOOGLE_MAPS_API_KEY = "${googleMapsKey}"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bbr',
        'USER': 'bbr',
        'PASSWORD':'${dbPasswordBbr}',
        'HOST':'${dbHost}',
        'PORT':'5432',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = 'http://${prefix}-site-media.s3-website.eu-west-2.amazonaws.com/'

NOTIFICATIONS_ENABLED = True
NOTIFICATION_TOPIC_ARN = "${notificationTopicArn}"
