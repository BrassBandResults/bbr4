# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^bands/$', views.bands_home),
    url(r'^bands/([\w\-]+)/$', views.band_compare),
    url(r'^bands/([\w\-]+)/([\w\-]+)/$', views.bands_compare),
    url(r'^bands/([\w\-]+)/([\w\-]+)/([\w\-]+)/$', views.bands_compare_contest),
    url(r'^conductors/$', views.conductors_home),
    url(r'^conductors/([\w\-]+)/$', views.conductor_compare),
    url(r'^conductors/([\w\-]+)/([\w\-]+)/$', views.conductors_compare),
    url(r'^conductors/([\w\-]+)/([\w\-]+)/([\w\-]+)/$', views.conductors_compare_contest),
]
