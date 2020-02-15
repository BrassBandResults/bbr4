# (c) 2019 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^section/([a-zA-Z_]+).json', views.jsonSection),
    url(r'^status/([a-zA-Z_]+).json', views.jsonStatus),
    url(r'^venues/Venues.json', views.jsonVenues),
]
