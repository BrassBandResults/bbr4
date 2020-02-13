# (c) 2019 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^section/([a-zA-Z_]+).json', views.jsonSection),
    url(r'^status/([a-zA-Z_]+).json', views.jsonStatus),

#    url(r'^venues/$', views.home_venues),
#    url(r'^band/([0-9a-z\-]+)/$', views.specific_band),
#    url(r'^venue/([0-9a-z\-]+)/$', views.specific_venue),
#    url(r'^band/([0-9a-z\-]+)/map_script.js$', views.specific_band_map_script),
#    url(r'^region/([0-9a-z\-]+)/map_script.js$', views.specific_region_map_script),
#    url(r'^venue/([0-9a-z\-]+)/map_script.js$', views.specific_venue_map_script),
#    url(r'^contest/event/(\d+)/map_script.js$', views.specific_contest_event_map_script),
#    url(r'^map_script.js$', views.map_script),
#    url(r'^addband/$', views.add_band),
#    url(r'^search/$', views.search_map),
#    url(r'^search/map_script.js$', views.map_script_search),
#    url(r'^coordwrong/$', views.move_band),
#    url(r'^coordwrong/([0-9a-z\-]+)/$', views.move_specific_band),
#    url(r'^coordwrong/([0-9a-z\-]+)/saved/$', views.move_specific_band_done),
]
