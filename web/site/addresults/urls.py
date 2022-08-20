# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.enter_contest_name),
    re_path(r'^whitfriday/$', views.whitfriday),
    re_path(r'^([\w-]+)/contest-type/$', views.enter_contest_type),
    re_path(r'^([\w-]+)/$',views.enter_contest_date),
    re_path(r'^([\w-]+)/([\d-]+)/$', views.enter_test_piece),
    re_path(r'^([\w-]+)/([\d-]+)/3/$', views.enter_composer),
    re_path(r'^([\w-]+)/([\d-]+)/4/$', views.enter_venue),
    re_path(r'^([\w-]+)/([\d-]+)/5/$', views.enter_results),
    re_path(r'^([\w-]+)/([\d-]+)/amend/$', views.amend_results),
    re_path(r'^([\w-]+)/([\d-]+)/6/$', views.enter_adjudicators),
    re_path(r'^([\w-]+)/([\d-]+)/6/remove_adjudicator/(\d+)/$', views.remove_adjudicator),
    re_path(r'^([\w-]+)/([\d-]+)/7/$', views.enter_notes),
#    re_path(r'^rpc/(\w+)/$', views.rpc),
    re_path(r'^exists/([\w-]+)/([\d-]+)/$', views.exists),
]