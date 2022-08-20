# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved


from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^([A-Za-z0-9]+)/$', views.list),
    re_path(r'^([A-Za-z0-9]+)/conductor/([-\w]+)/$', views.list_filter_conductor),
    re_path(r'^([A-Za-z0-9]+)/band/([-\w]+)/$', views.list_filter_band),
    re_path(r'^([A-Za-z0-9]+)/contest/([-\w]+)/$', views.list_filter_contest),
    re_path(r'^([A-Za-z0-9]+)/group/([-\w]+)/$', views.list_filter_group),
    re_path(r'^([A-Za-z0-9]+)/chartdata/$', views.user_chart_json),
]
