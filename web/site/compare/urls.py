# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^bands/$', views.bands_home),
    re_path(r'^bands/([\w\-]+)/$', views.band_compare),
    re_path(r'^bands/([\w\-]+)/([\w\-]+)/$', views.bands_compare),
    re_path(r'^bands/([\w\-]+)/([\w\-]+)/([\w\-]+)/$', views.bands_compare_contest),
    re_path(r'^conductors/$', views.conductors_home),
    re_path(r'^conductors/([\w\-]+)/$', views.conductor_compare),
    re_path(r'^conductors/([\w\-]+)/([\w\-]+)/$', views.conductors_compare),
    re_path(r'^conductors/([\w\-]+)/([\w\-]+)/([\w\-]+)/$', views.conductors_compare_contest),
]
