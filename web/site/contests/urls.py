# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path
from django.contrib.sitemaps.views import sitemap

from contests.sitemap import ContestSitemap

from . import views


sitemaps = {
  'contests' : ContestSitemap,
}

urlpatterns = [
    re_path(r'^$', views.contest_list),
    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^groups/$', views.contest_groups),
    re_path(r'^groups/delete/(\d+)/$', views.delete_contest_group),
    re_path(r'^filter/([A-Z]+)/$', views.contest_list_filter_letter),
    re_path(r'^edit/([-a-zA-Z0-9]+)/$', views.edit_contest),
    re_path(r'^delete/([-a-zA-Z0-9]+)/$', views.delete_contest),
    re_path(r'^AddFutureEvent/$', views.add_future_event_popup),
    re_path(r'^result/edit/(\w+)/$', views.edit_result),
    re_path(r'^result/delete/(\w+)/$', views.delete_result),
    re_path(r'^([a-z0-9\-]+)/$', views.single_contest),
    re_path(r'^([A-Z0-9\-]+)/$', views.single_contest_group),
    re_path(r'^([a-z0-9\-]+)/talk/$', views.talk_contest),
    re_path(r'^([a-z0-9\-]+)/talk/edit/$', views.talk_edit_contest),
    re_path(r'^([A-Z0-9\-]+)/talk/$', views.talk_group),
    re_path(r'^([A-Z0-9\-]+)/talk/edit/$', views.talk_edit_group),
    re_path(r'^([A-Z0-9\-]+)/(\d{4})/$', views.single_contest_group_year),
    re_path(r'^([A-Z0-9\-]+)/([\d\-]+)/$', views.group_results),
    re_path(r'^([\w\-]+)/addfuture/$', views.add_future_event),
    re_path(r'^([\w\-]+)/deletefuture/(\d+)/$', views.delete_future_event),
    re_path(r'^([\w\-]+)/draw/(\d+)/$', views.single_contest_event_draw),
    re_path(r'^([\w\-]+)/position/([\dWD]+)/$', views.single_contest_event_position),
    re_path(r'^([\w\-]+)/([\d\-]+)/$', views.single_contest_event),
    re_path(r'^([\w\-]+)/([\d\-]+)/form/$', views.single_contest_event_form_guide),
    re_path(r'^([\w\-]+)/([\d\-]+)/entertainments/$', views.single_contest_edit_extra_pieces),
    re_path(r'^([\w\-]+)/([\d\-]+)/entertainments/delete/(\d+)/$', views.single_contest_delete_extra_piece),
    re_path(r'^([\w\-]+)/([\d\-]+)/AssignPositionFromPoints/$', views.assign_position_from_points),
    re_path(r'^([\w\-]+)/([\d\-]+)/Compress/$', views.single_contest_event_compress),
    re_path(r'^([\w\-]+)/([\d\-]+)/PropagateMarch/$', views.single_contest_event_propagate_march),
    re_path(r'^([\w\-]+)/([\d\-]+)/map/$', views.single_contest_event_map),
    re_path(r'^([\w\-]+)/([\d\-]+)/competitors/$', views.single_contest_event_competitors),
    re_path(r'^([\w\-]+)/([\d\-]+)/AddToContestHistory/$', views.add_to_contest_history),
    re_path(r'^([\w\-]+)/([\d\-]+)/TakeOwnership/$', views.take_ownership),
    re_path(r'^([\w\-]+)/([\d\-]+)/autodraw/([\w\-]+)/(\d+)/$', views.autodraw),
    re_path(r'^([\w\-]+)/([\d\-]+)/stars/$', views.stars),
    re_path(r'^([\w\-]+)/([\d\-]+)/AddToContestHistory/(\d+)/$', views.add_result_to_contest_history),
    re_path(r'^([\w\-]+)/([\d\-]+)/edit/(\d+)/$', views.edit_event),
]
