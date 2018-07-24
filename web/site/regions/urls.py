# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.conf.urls import url
#from django.contrib.sitemaps.views import sitemap

#from bands.sitemap import BandSitemap

from . import views


#sitemaps = {
#  'bands' : BandSitemap,
#}

urlpatterns = [
    url(r'^$', views.region_list),
    url(r'^([\w\-]+)/$', views.single_region),
    url(r'^([\w\-]+)/links/$', views.region_links),
]    
 
