# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved


from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^band/([\w\-]+)/results/(1|2)/$', views.band_results),
]
