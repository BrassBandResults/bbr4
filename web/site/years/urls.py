# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.year_list, name='year_list'),
    url(r'^region/([-\w]+)/$', views.year_list_region, name='year_list_region'),
    url(r'^(\d{4})/$', views.single_year, name='single_year'),
    url(r'^(\d{4})/region/([-\w]+)/$', views.single_year_region, name='single_year_region'),
]