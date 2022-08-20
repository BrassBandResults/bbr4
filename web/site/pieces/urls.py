# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.piece_list),
    re_path(r'^add/$', views.add_piece),
    re_path(r'^options/$', views.piece_options),
    re_path(r'^edit/([-\w]+)/$', views.edit_piece),
    re_path(r'^BySection/$', views.pieces_by_section),
    re_path(r'^BestOwnChoice/$', views.best_own_choice),
    re_path(r'^([A-Z0]+)/$', views.piece_list_filter_letter),
    re_path(r'^([\w\-]+)/$', views.single_piece),
]
