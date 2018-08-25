# (c) 2018 Tim Sawyer, All Rights Reserved

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    'accounts',
    'addresults',
    'addwhitfriday',
    'adjudicators',
    'api',
    'audit',
    'badges',
    'bandmap',
    'bands',
    'classifieds',
    'compare',
    'composers',
    'conductors',
    'contest_calendar',
    'contests',
    'embed',
    'feedback',
    'feeds',
    'home',
    'usermessages',
    'leaderboard',
    'move',
    'myresults',
    'notification',
    'payments',
    'people',
    'pieces',
    'regions',
    'search',
    'sections',
    'statistics',
    'tags',
    'users',
    'venues',
    'years',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bbr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bbr.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LOGIN_REDIRECT_URL = '/'

SUFFIXES = (
            ('Jnr','Jnr'),
            ('Snr','Snr'),
            ('I','I'),
            ('II','II'),
            ('III','III'),
           )

OWN_CHOICE_POINTS = {1:10, 2:5, 3:3}

UNKNOWN_PERSON_ID = 310730

ACCOUNT_ACTIVATION_DAYS = 3

