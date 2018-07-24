# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(\d+)/$', views.show),
    url(r'^create/(\w+)/$', views.create),
    url(r'^create/(\w+)/([A-Za-z0-9 :-]+)/$', views.create_with_subject),
    url(r'^delete/(\d+)/$', views.delete),
]

