# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.feedback),
    url(r'^queue/$', views.queue),
    url(r'^admin/$', views.admin_queue),
    url(r'^thanks/$', views.thanks),
    url(r'^detail/(\d+)/$', views.feedback_detail),
    url(r'^ip/([.\d]+)/$', views.feedback_for_ip),
]
