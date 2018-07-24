# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.venue_list, name="venue_list"),
    url(r'^add/$', views.add_venue, name="add_venue"),
    url(r'^options/$', views.venue_options, name="venue_options"),
    url(r'^edit/([\w\-]+)/$', views.edit_venue, name="edit_venue"),
    url(r'^([\w\-]+)/$', views.single_venue, name="single_venue"),
    url(r'^([\w\-]+)/aliases/$', views.single_venue_aliases, name="single_venue_aliases"),
    url(r'^([\w\-]+)/aliases/(\d+)/delete/$', views.single_venue_alias_delete, name="venue_alias_delete"),
    url(r'^([\w\-]+)/([\w\-]+)/$', views.single_venue_event, name='venue_events'),
    
]