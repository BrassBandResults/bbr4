# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^([\w\-]+)/$', views.single_conductor),
    re_path(r'^([\w\-]+)/tag/([A-Za-z0-9\-]+)/$', views.single_conductor_filter_tag),
    re_path(r'^([\w\-]+)/([a-z0-9\-]+)/$', views.single_conductor_filter),
    re_path(r'^([\w\-]+)/([A-Z0-9\-]+)/$', views.single_conductor_filter_group),
]
