# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.home),
    re_path(r'^(\d+)/(\d+)/$', views.calendar),
    re_path(r'^date/(\d+)/$', views.contests_for_year),
    re_path(r'^date/(\d+)/(\d+)/$', views.contests_for_month),
    re_path(r'^date/(\d+)/(\d+)/(\d+)/$', views.contests_for_day),
]