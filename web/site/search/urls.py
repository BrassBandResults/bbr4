# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.search),
]
