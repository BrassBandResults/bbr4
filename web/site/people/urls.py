# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap

from people.sitemap import PeopleSitemap

from . import views


sitemaps = {
  'people' : PeopleSitemap,
}

urlpatterns = [
    url(r'^$', views.people_list),
    url(r'^hashes/letter.json$', views.people_hash_by_letter),
    url(r'^hashes/(\w).json$', views.people_list_by_letter),
    url(r'^([A-Z]+)/$', views.people_list_filter_letter),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^about_profile/$', views.about_profile),
    url(r'^([\w\-]+)/newclassified/$', views.new_classified),
    url(r'^([\w\-]+)/newclassified/too_many/$', views.too_many_classified),
    url(r'^([\w\-]+)/edit_classified/$', views.edit_classified),    
    url(r'^add/$', views.add_person),
    url(r'^winners/$', views.contest_winners),
    url(r'^edit/([-\w]+)/$', views.edit_person),
    url(r'^options/$', views.people_options),
    url(r'^options.json/$', views.people_options_json),
    url(r'^([\w\-]+)/$', views.single_person),
    url(r'^([\w\-]+)/aliases/$', views.single_person_aliases),
    url(r'^([\w\-]+)/aliases/(\d+)/show/$', views.single_person_alias_show),
    url(r'^([\w\-]+)/aliases/(\d+)/hide/$', views.single_person_alias_hide),
    url(r'^([\w\-]+)/aliases/(\d+)/delete/$', views.single_person_alias_delete),
    url(r'^([\w\-]+)/csv/$', views.single_person_csv),
    url(r'^chartdata/([\w\-]+)/$', views.chart_json),
    url(r'^chartdata/([\w\-]+)/([a-z0-9\-]+)/$', views.chart_json_filter),
    url(r'^chartdata/([\w\-]+)/([A-Z0-9\-]+)/$', views.chart_json_filter_group),
    url(r'^([\w\-]+)/tag/([A-Za-z0-9\-]+)/$', views.single_person_filter_tag),
    url(r'^([\w\-]+)/([a-z0-9\-]+)/$', views.single_person_filter_contest),
    url(r'^([\w\-]+)/([A-Z0-9\-]+)/$', views.single_person_filter_group),
    
]
