# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^(\d+)/(\d+)/$', views.calendar),
    url(r'^date/(\d+)/$', views.contests_for_year),
    url(r'^date/(\d+)/(\d+)/$', views.contests_for_month),
    url(r'^date/(\d+)/(\d+)/(\d+)/$', views.contests_for_day),
]