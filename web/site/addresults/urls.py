# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.enter_contest_name),
    url(r'^whitfriday/$', views.whitfriday),
    url(r'^([\w-]+)/contest-type/$', views.enter_contest_type),
    url(r'^([\w-]+)/$',views.enter_contest_date),
    url(r'^([\w-]+)/([\d-]+)/$', views.enter_test_piece),
    url(r'^([\w-]+)/([\d-]+)/3/$', views.enter_composer),
    url(r'^([\w-]+)/([\d-]+)/4/$', views.enter_venue),
    url(r'^([\w-]+)/([\d-]+)/5/$', views.enter_results),
    url(r'^([\w-]+)/([\d-]+)/amend/$', views.amend_results),
    url(r'^([\w-]+)/([\d-]+)/6/$', views.enter_adjudicators),
    url(r'^([\w-]+)/([\d-]+)/6/remove_adjudicator/(\d+)/$', views.remove_adjudicator),
    url(r'^([\w-]+)/([\d-]+)/7/$', views.enter_notes),
#    url(r'^rpc/(\w+)/$', views.rpc),
    url(r'^exists/([\w-]+)/([\d-]+)/$', views.exists),
]