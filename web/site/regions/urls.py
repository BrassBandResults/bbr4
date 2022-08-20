# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.urls import re_path
#from django.contrib.sitemaps.views import sitemap

#from bands.sitemap import BandSitemap

from . import views


#sitemaps = {
#  'bands' : BandSitemap,
#}

urlpatterns = [
    re_path(r'^$', views.region_list),
    re_path(r'^([\w\-]+)/$', views.single_region),
    re_path(r'^([\w\-]+)/links/$', views.region_links),
]    
 
