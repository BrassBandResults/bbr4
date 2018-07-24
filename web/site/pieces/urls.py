# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.piece_list),
    url(r'^add/$', views.add_piece),
    url(r'^options/$', views.piece_options),
    url(r'^edit/([-\w]+)/$', views.edit_piece),
    url(r'^BySection/$', views.pieces_by_section),
    url(r'^BestOwnChoice/$', views.best_own_choice),
    url(r'^([A-Z0]+)/$', views.piece_list_filter_letter),
    url(r'^([\w\-]+)/$', views.single_piece),
]
