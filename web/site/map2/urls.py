# (c) 2019 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.home),
    re_path(r'^section/([a-zA-Z_]+).json', views.jsonSection),
    re_path(r'^status/([a-zA-Z_]+).json', views.jsonStatus),
    re_path(r'^venues/Venues.json', views.jsonVenues),
]
