# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^([A-Za-z0-9]+)/$', views.list),
    url(r'^([A-Za-z0-9]+)/conductor/([-\w]+)/$', views.list_filter_conductor),
    url(r'^([A-Za-z0-9]+)/band/([-\w]+)/$', views.list_filter_band),
    url(r'^([A-Za-z0-9]+)/contest/([-\w]+)/$', views.list_filter_contest),
    url(r'^([A-Za-z0-9]+)/group/([-\w]+)/$', views.list_filter_group),
    url(r'^([A-Za-z0-9]+)/chartdata/$', views.user_chart_json),
]
