# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^(\d+)/$', views.show),
    re_path(r'^create/(\w+)/$', views.create),
    re_path(r'^create/(\w+)/([A-Za-z0-9 :-]+)/$', views.create_with_subject),
    re_path(r'^delete/(\d+)/$', views.delete),
]

