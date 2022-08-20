# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.urls import re_path
#from django.contrib.sitemaps.views import sitemap

#from bands.sitemap import BandSitemap

from . import views


#sitemaps = {
#  'bands' : BandSitemap,
#}

urlpatterns = [
    re_path(r'^$', views.bands_list),
  #  re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^add/$', views.add_band),
    re_path(r'^options/$', views.band_options),
    re_path(r'^edit/([-\w]+)/$', views.edit_band),
    re_path(r'^winners/$', views.contest_winners),
    re_path(r'^([A-Z0]+)/$', views.bands_list),
    re_path(r'^([\w\-]+)/$', views.single_band),
    re_path(r'^([\w\-]+)/delete/$', views.delete_single_band),
    re_path(r'^([\w\-]+)/aliases/$', views.single_band_aliases),
    re_path(r'^([\w\-]+)/aliases/(\d+)/show/$', views.single_band_alias_show),
    re_path(r'^([\w\-]+)/aliases/(\d+)/hide/$', views.single_band_alias_hide),
    re_path(r'^([\w\-]+)/aliases/(\d+)/delete/$',views.single_band_alias_delete),
    re_path(r'^([\w\-]+)/WhitFridayConductors/$', views.update_whit_friday_conductors),
    re_path(r'^([\w\-]+)/talk/$', views.talk),
    re_path(r'^([\w\-]+)/talk/edit/$', views.talk_edit),
    re_path(r'^([\w\-]+)/embed/$', views.band_results_embed),
    re_path(r'^([\w\-]+)/csv/$', views.band_results_csv),
    re_path(r'^chartdata/([\w\-]+)/$', views.chart_json),
    re_path(r'^chartdata/([\w\-]+)/([a-z0-9\-]+)/$', views.chart_json_filter),
    re_path(r'^chartdata/([\w\-]+)/([A-Z0-9\-]+)/$', views.chart_json_filter_group),
    re_path(r'^([\w\-]+)/tag/([A-Za-z0-9\-]+)/$', views.single_band_filter_tag),
    re_path(r'^([\w\-]+)/([a-z0-9\-]+)/$', views.single_band_filter),
    re_path(r'^([\w\-]+)/([A-Z0-9\-]+)/$', views.single_band_filter_group),
]    
 
