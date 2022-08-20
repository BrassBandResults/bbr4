# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.feedback),
    re_path(r'^queue/$', views.queue),
    re_path(r'^admin/$', views.admin_queue),
    re_path(r'^thanks/$', views.thanks),
    re_path(r'^detail/(\d+)/$', views.feedback_detail),
    re_path(r'^ip/([.\d]+)/$', views.feedback_for_ip),
]
