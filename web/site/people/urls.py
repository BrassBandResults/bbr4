# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path
from django.contrib.sitemaps.views import sitemap

from people.sitemap import PeopleSitemap

from . import views


sitemaps = {
  'people' : PeopleSitemap,
}

urlpatterns = [
    re_path(r'^$', views.people_list),
    re_path(r'^hashes/letter.json$', views.people_hash_by_letter),
    re_path(r'^hashes/(\w).json$', views.people_list_by_letter),
    re_path(r'^([A-Z]+)/$', views.people_list_filter_letter),
    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^about_profile/$', views.about_profile),
    re_path(r'^([\w\-]+)/newclassified/$', views.new_classified),
    re_path(r'^([\w\-]+)/newclassified/too_many/$', views.too_many_classified),
    re_path(r'^([\w\-]+)/edit_classified/$', views.edit_classified),
    re_path(r'^add/$', views.add_person),
    re_path(r'^winners/$', views.contest_winners),
    re_path(r'^bands/$', views.number_bands),
    re_path(r'^edit/([-\w]+)/$', views.edit_person),
    re_path(r'^options/$', views.people_options),
    re_path(r'^options.json/$', views.people_options_json),
    re_path(r'^([\w\-]+)/$', views.single_person),
    re_path(r'^([\w\-]+)/aliases/$', views.single_person_aliases),
    re_path(r'^([\w\-]+)/aliases/(\d+)/show/$', views.single_person_alias_show),
    re_path(r'^([\w\-]+)/aliases/(\d+)/hide/$', views.single_person_alias_hide),
    re_path(r'^([\w\-]+)/aliases/(\d+)/delete/$', views.single_person_alias_delete),
    re_path(r'^([\w\-]+)/csv/$', views.single_person_csv),
    re_path(r'^chartdata/([\w\-]+)/$', views.chart_json),
    re_path(r'^chartdata/([\w\-]+)/([a-z0-9\-]+)/$', views.chart_json_filter),
    re_path(r'^chartdata/([\w\-]+)/([A-Z0-9\-]+)/$', views.chart_json_filter_group),
    re_path(r'^([\w\-]+)/tag/([A-Za-z0-9\-]+)/$', views.single_person_filter_tag),
    re_path(r'^([\w\-]+)/([a-z0-9\-]+)/$', views.single_person_filter_contest),
    re_path(r'^([\w\-]+)/([A-Z0-9\-]+)/$', views.single_person_filter_group),

]
