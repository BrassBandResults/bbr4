# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.home),
    re_path(r'^venues/$', views.home_venues),
    re_path(r'^band/([0-9a-z\-]+)/$', views.specific_band),
    re_path(r'^venue/([0-9a-z\-]+)/$', views.specific_venue),
    re_path(r'^band/([0-9a-z\-]+)/map_script.js$', views.specific_band_map_script),
    re_path(r'^region/([0-9a-z\-]+)/map_script.js$', views.specific_region_map_script),
    re_path(r'^venue/([0-9a-z\-]+)/map_script.js$', views.specific_venue_map_script),
    re_path(r'^contest/event/(\d+)/map_script.js$', views.specific_contest_event_map_script),
    re_path(r'^map_script.js$', views.map_script),
    re_path(r'^addband/$', views.add_band),
    re_path(r'^search/$', views.search_map),
    re_path(r'^search/map_script.js$', views.map_script_search),
    re_path(r'^coordwrong/$', views.move_band),
    re_path(r'^coordwrong/([0-9a-z\-]+)/$', views.move_specific_band),
    re_path(r'^coordwrong/([0-9a-z\-]+)/saved/$', views.move_specific_band_done),
]

