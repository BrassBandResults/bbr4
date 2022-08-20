# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.year_list, name='year_list'),
    re_path(r'^region/([-\w]+)/$', views.year_list_region, name='year_list_region'),
    re_path(r'^(\d{4})/$', views.single_year, name='single_year'),
    re_path(r'^(\d{4})/region/([-\w]+)/$', views.single_year_region, name='single_year_region'),
]