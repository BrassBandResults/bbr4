# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.conf.urls import url
#from django.contrib.sitemaps.views import sitemap

#from bands.sitemap import BandSitemap

from . import views


#sitemaps = {
#  'bands' : BandSitemap,
#}

urlpatterns = [
    url(r'^$', views.bands_list),
  #  url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^add/$', views.add_band),
    url(r'^options/$', views.band_options),
    url(r'^edit/([-\w]+)/$', views.edit_band),
    url(r'^winners/$', views.contest_winners),
    url(r'^([A-Z0]+)/$', views.bands_list),
    url(r'^([\w\-]+)/$', views.single_band),
    url(r'^([\w\-]+)/delete/$', views.delete_single_band),
    url(r'^([\w\-]+)/aliases/$', views.single_band_aliases),
    url(r'^([\w\-]+)/aliases/(\d+)/show/$', views.single_band_alias_show),
    url(r'^([\w\-]+)/aliases/(\d+)/hide/$', views.single_band_alias_hide),
    url(r'^([\w\-]+)/aliases/(\d+)/delete/$',views.single_band_alias_delete),
    url(r'^([\w\-]+)/WhitFridayConductors/$', views.update_whit_friday_conductors),
    url(r'^([\w\-]+)/talk/$', views.talk),
    url(r'^([\w\-]+)/talk/edit/$', views.talk_edit),
    url(r'^([\w\-]+)/embed/$', views.band_results_embed),
    url(r'^([\w\-]+)/csv/$', views.band_results_csv),
    url(r'^chartdata/([\w\-]+)/$', views.chart_json),
    url(r'^chartdata/([\w\-]+)/([a-z0-9\-]+)/$', views.chart_json_filter),
    url(r'^chartdata/([\w\-]+)/([A-Z0-9\-]+)/$', views.chart_json_filter_group),
    url(r'^([\w\-]+)/tag/([A-Za-z0-9\-]+)/$', views.single_band_filter_tag),
    url(r'^([\w\-]+)/([a-z0-9\-]+)/$', views.single_band_filter),
    url(r'^([\w\-]+)/([A-Z0-9\-]+)/$', views.single_band_filter_group),
]    
 
