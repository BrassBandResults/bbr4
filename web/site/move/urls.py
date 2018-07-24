# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from move.views import move_bands
from move.views import move_people
from move.views import move_venues
from move.views import move_pieces

urlpatterns = [
    url(r'^bands/$', move_bands.list_merge_requests),
    url(r'^bands/merge/(\d+)/$', move_bands.merge_action),
    url(r'^bands/reject_merge/(\d+)/$', move_bands.reject_merge),    
    url(r'^bands/([-\w]+)/move_results/$', move_bands.merge_request),
                       
    url(r'^people/$', move_people.list_merge_requests),
    url(r'^people/merge/(\d+)/$', move_people.merge_action),
    url(r'^people/reject_merge/(\d+)/$', move_people.reject_merge),    
    url(r'^people/([-\w]+)/move_person/$', move_people.merge_request),
 
    url(r'^venues/$', move_venues.list_merge_requests),
    url(r'^venues/merge/(\d+)/$', move_venues.merge_action),
    url(r'^venues/reject_merge/(\d+)/$', move_venues.reject_merge),    
    url(r'^venues/([-\w]+)/move_contests/$', move_venues.merge_request),
    
    url(r'^pieces/$', move_pieces.list_merge_requests),
    url(r'^pieces/merge/(\d+)/$', move_pieces.merge_action),
    url(r'^pieces/reject_merge/(\d+)/$', move_pieces.reject_merge),    
    url(r'^pieces/([-\w]+)/move_pieces/$', move_pieces.merge_request),
 
]

