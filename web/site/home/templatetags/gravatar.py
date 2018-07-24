# (c) 2012,2018 Tim Sawyer, All Rights Reserved

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.contrib.auth.models import User
from django.conf import settings

import urllib, hashlib

GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "http://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", "identicon")

register = template.Library()

def get_user(user):
    if not isinstance(user, User):
        user = User.objects.get(username=user)
    return user

def gravatar_for_email(email, size=80):
    url = "%savatar/%s/?" % (GRAVATAR_URL_PREFIX, hashlib.md5(email.lower().encode('utf-8')).hexdigest())
    url += urllib.parse.urlencode({"s": str(size), "default": GRAVATAR_DEFAULT_IMAGE})
    return url

def gravatar_for_user(user, size=80):
    user = get_user(user)
    return gravatar_for_email(user.email, size)

def gravatar_img_for_user(user, size=80):
    user = get_user(user)
    url = gravatar_for_user(user)
    return mark_safe("""<img src="%s" alt="Avatar for %s" height="%s" width="%s" border="0"/>""" % (escape(url), user.username, size, size))

def gravatar(user, size=80):
    # backward compatibility
    return gravatar_img_for_user(user, size)

register.simple_tag(gravatar)
register.simple_tag(gravatar_for_user)
register.simple_tag(gravatar_for_email)
register.simple_tag(gravatar_img_for_user)
