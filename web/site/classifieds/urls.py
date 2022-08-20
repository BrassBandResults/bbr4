# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^band/([-\w]+)/$', views.this_is_my_band),
    re_path(r'^(\w+)/([-\w]+)/$', views.this_is_me),
    re_path(r'^band/([-\w]+)/signup/$', views.signup_band),
    re_path(r'^(\w+)/([-\w]+)/signup/$', views.signup),
    re_path(r'^(\w+)/([-\w]+)/payment/$', views.payment),
    re_path(r'^paid/$', views.paid),
    re_path(r'^paid_band/$', views.paid_band),
    re_path(r'^about_profile/$', views.about_profile),
    re_path(r'^about_band_profile/$', views.about_band_profile),
    re_path(r'^owned_by_other_user/(\w+)/([-\w]+)/$', views.owned_by_another_user),
]

