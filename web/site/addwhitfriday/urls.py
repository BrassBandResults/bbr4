# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.enter_contest_name),
    url(r'^([\w-]+)/$', views.enter_contest_date),
    url(r'^([\w-]+)/([\d-]+)/$', views.enter_results),
]
