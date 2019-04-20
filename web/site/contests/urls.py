# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap

from contests.sitemap import ContestSitemap

from . import views


sitemaps = {
  'contests' : ContestSitemap,
}

urlpatterns = [
    url(r'^$', views.contest_list),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^groups/$', views.contest_groups),
    url(r'^groups/delete/(\d+)/$', views.delete_contest_group),
    url(r'^filter/([A-Z]+)/$', views.contest_list_filter_letter),
    url(r'^edit/([-a-zA-Z0-9]+)/$', views.edit_contest),
    url(r'^delete/([-a-zA-Z0-9]+)/$', views.delete_contest),
    url(r'^AddFutureEvent/$', views.add_future_event_popup),
    url(r'^result/edit/(\w+)/$', views.edit_result),
    url(r'^result/delete/(\w+)/$', views.delete_result),
    url(r'^([a-z0-9\-]+)/$', views.single_contest),
    url(r'^([A-Z0-9\-]+)/$', views.single_contest_group),
    url(r'^([a-z0-9\-]+)/talk/$', views.talk_contest),
    url(r'^([a-z0-9\-]+)/talk/edit/$', views.talk_edit_contest),
    url(r'^([A-Z0-9\-]+)/talk/$', views.talk_group),
    url(r'^([A-Z0-9\-]+)/talk/edit/$', views.talk_edit_group),
    url(r'^([A-Z0-9\-]+)/(\d{4})/$', views.single_contest_group_year),
    url(r'^([A-Z0-9\-]+)/([\d\-]+)/$', views.group_results),
    url(r'^([\w\-]+)/addfuture/$', views.add_future_event),
    url(r'^([\w\-]+)/deletefuture/(\d+)/$', views.delete_future_event),
    url(r'^([\w\-]+)/draw/(\d+)/$', views.single_contest_event_draw),
    url(r'^([\w\-]+)/position/([\dWD]+)/$', views.single_contest_event_position),
    url(r'^([\w\-]+)/([\d\-]+)/$', views.single_contest_event),
    url(r'^([\w\-]+)/([\d\-]+)/form/$', views.single_contest_event_form_guide),
    url(r'^([\w\-]+)/([\d\-]+)/entertainments/$', views.single_contest_edit_extra_pieces),
    url(r'^([\w\-]+)/([\d\-]+)/entertainments/delete/(\d+)/$', views.single_contest_delete_extra_piece),
    url(r'^([\w\-]+)/([\d\-]+)/AssignPositionFromPoints/$', views.assign_position_from_points),
    url(r'^([\w\-]+)/([\d\-]+)/Compress/$', views.single_contest_event_compress),
    url(r'^([\w\-]+)/([\d\-]+)/PropagateMarch/$', views.single_contest_event_propagate_march),
    url(r'^([\w\-]+)/([\d\-]+)/map/$', views.single_contest_event_map),
    url(r'^([\w\-]+)/([\d\-]+)/competitors/$', views.single_contest_event_competitors),
    url(r'^([\w\-]+)/([\d\-]+)/programme/$', views.single_contest_event_programme),
    url(r'^([\w\-]+)/([\d\-]+)/AddToContestHistory/$', views.add_to_contest_history),
    url(r'^([\w\-]+)/([\d\-]+)/TakeOwnership/$', views.take_ownership),
    url(r'^([\w\-]+)/([\d\-]+)/autodraw/([\w\-]+)/(\d+)/$', views.autodraw),
    url(r'^([\w\-]+)/([\d\-]+)/stars/$', views.stars),
    url(r'^([\w\-]+)/([\d\-]+)/AddToContestHistory/(\d+)/$', views.add_result_to_contest_history),
    url(r'^([\w\-]+)/([\d\-]+)/edit/(\d+)/$', views.edit_event),
]
