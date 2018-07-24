# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^band/([-\w]+)/$', views.this_is_my_band),
    url(r'^(\w+)/([-\w]+)/$', views.this_is_me),
    url(r'^band/([-\w]+)/signup/$', views.signup_band),
    url(r'^(\w+)/([-\w]+)/signup/$', views.signup),
    url(r'^(\w+)/([-\w]+)/payment/$', views.payment),
    url(r'^paid/$', views.paid),
    url(r'^paid_band/$', views.paid_band),
    url(r'^about_profile/$', views.about_profile),
    url(r'^about_band_profile/$', views.about_band_profile),
    url(r'^owned_by_other_user/(\w+)/([-\w]+)/$', views.owned_by_another_user),
]

