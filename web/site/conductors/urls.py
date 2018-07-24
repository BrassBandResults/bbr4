# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^([\w\-]+)/$', views.single_conductor),
    url(r'^([\w\-]+)/tag/([A-Za-z0-9\-]+)/$', views.single_conductor_filter_tag),
    url(r'^([\w\-]+)/([a-z0-9\-]+)/$', views.single_conductor_filter),
    url(r'^([\w\-]+)/([A-Z0-9\-]+)/$', views.single_conductor_filter_group),
]
