# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^new/$', views.new_tag),
    url(r'^([\w\-]+)/$', views.single_tag),
    url(r'^([\w\-]+)/remove/([\w]+)/([\w\-]+)/$', views.remove_tag),
]