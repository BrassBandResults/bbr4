# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.venue_list, name="venue_list"),
    re_path(r'^add/$', views.add_venue, name="add_venue"),
    re_path(r'^options/$', views.venue_options, name="venue_options"),
    re_path(r'^edit/([\w\-]+)/$', views.edit_venue, name="edit_venue"),
    re_path(r'^([\w\-]+)/$', views.single_venue, name="single_venue"),
    re_path(r'^([\w\-]+)/aliases/$', views.single_venue_aliases, name="single_venue_aliases"),
    re_path(r'^([\w\-]+)/aliases/(\d+)/delete/$', views.single_venue_alias_delete, name="venue_alias_delete"),
    re_path(r'^([\w\-]+)/([\w\-]+)/$', views.single_venue_event, name='venue_events'),
    
]