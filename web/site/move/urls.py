# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from move.views import move_bands
from move.views import move_people
from move.views import move_venues
from move.views import move_pieces

urlpatterns = [
    re_path(r'^bands/$', move_bands.list_merge_requests),
    re_path(r'^bands/merge/(\d+)/$', move_bands.merge_action),
    re_path(r'^bands/reject_merge/(\d+)/$', move_bands.reject_merge),    
    re_path(r'^bands/([-\w]+)/move_results/$', move_bands.merge_request),
                       
    re_path(r'^people/$', move_people.list_merge_requests),
    re_path(r'^people/merge/(\d+)/$', move_people.merge_action),
    re_path(r'^people/reject_merge/(\d+)/$', move_people.reject_merge),    
    re_path(r'^people/([-\w]+)/move_person/$', move_people.merge_request),
 
    re_path(r'^venues/$', move_venues.list_merge_requests),
    re_path(r'^venues/merge/(\d+)/$', move_venues.merge_action),
    re_path(r'^venues/reject_merge/(\d+)/$', move_venues.reject_merge),    
    re_path(r'^venues/([-\w]+)/move_contests/$', move_venues.merge_request),
    
    re_path(r'^pieces/$', move_pieces.list_merge_requests),
    re_path(r'^pieces/merge/(\d+)/$', move_pieces.merge_action),
    re_path(r'^pieces/reject_merge/(\d+)/$', move_pieces.reject_merge),    
    re_path(r'^pieces/([-\w]+)/move_pieces/$', move_pieces.merge_request),
 
]

