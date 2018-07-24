# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  # noqa