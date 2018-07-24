# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved


from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^bands/english/active/$', views.bands_english_active),
    url(r'^bands/english/none/$', views.bands_english_none),
]
