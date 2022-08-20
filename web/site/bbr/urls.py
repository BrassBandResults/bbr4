# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

"""bbr4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.contrib import admin

from home import views as home_views
from accounts import views as account_views
from users import views as user_views

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView

from django.contrib.auth import views as auth_views

urlpatterns = [
    re_path(r'^$', home_views.home),
    re_path(r'^faq/$', home_views.faq),
    re_path(r'^aboutus/$', home_views.about),
    re_path(r'^privacy/$', home_views.cookies),

    re_path(r'^bbradmin/', admin.site.urls),

    re_path(r'^addresults/', include('addresults.urls')),
    re_path(r'^addwhitfriday/', include('addwhitfriday.urls')),
    re_path(r'^adjudicators/', include('adjudicators.urls')),
    re_path(r'^api/', include('api.urls')),
    re_path(r'^badges/', include('badges.urls')),
    re_path(r'^bands/', include('bands.urls')),
    re_path(r'^calendar/', include('contest_calendar.urls')),
    re_path(r'^compare/', include('compare.urls')),
    re_path(r'^composers/', include('composers.urls')),
    re_path(r'^conductors/', include('conductors.urls')),
    re_path(r'^contests/', include('contests.urls')),
    re_path(r'^embed/', include('embed.urls')),
    re_path(r'^feedback/', include('feedback.urls')),
    re_path(r'^feeds/', include('feeds.urls')),
    re_path(r'^leaderboard/', include('leaderboard.urls')),
    re_path(r'^map/', include('bandmap.urls')),
    re_path(r'^map2/', include('map2.urls')),
    re_path(r'^messages/', include('usermessages.urls')),
    re_path(r'^move/', include('move.urls')),
    re_path(r'^myresults/', include('myresults.urls')),
    re_path(r'^people/', include('people.urls')),
    re_path(r'^pieces/', include('pieces.urls')),
    re_path(r'^regions/', include('regions.urls')),
    re_path(r'^search/', include('search.urls')),
    re_path(r'^sections/', include('sections.urls')),
    re_path(r'^statistics/', include('statistics.urls')),
    re_path(r'^tags/', include('tags.urls')),
    re_path(r'^users/', include('users.urls')),
    re_path(r'^venues/', include('venues.urls')),
    re_path(r'^years/', include('years.urls')),

    re_path(r'^sitemap.xml$', home_views.sitemap_index),
    re_path(r'^robots.txt$', home_views.robotstxt),
    re_path(r'^ads.txt$', home_views.adstxt),

    re_path(r'^accounts/login/$', LoginView.as_view(),  {'template_name': 'accounts/login.html'}),
    re_path(r'^accounts/logout/$', LogoutView.as_view(),  {'template_name': 'accounts/logout.html'}),
    re_path(r'^accounts/forgottenpassword/$', user_views.forgotten_password),
    re_path(r'^accounts/forgottenpassword/sent/$', user_views.forgotten_password_sent),
    re_path(r'^accounts/resetpassword/([A-Za-z0-9]+)/$', user_views.reset_password),
    re_path(r'^accounts/changepassword/$', PasswordChangeView.as_view(), {'template_name' : 'users/changepassword.html', 'post_change_redirect' : '/'}),

    re_path(r'^accounts/loginpro/$', LoginView.as_view(), {'template_name' : 'accounts/loginpro.html',}),
    re_path(r'^accounts/upgrade/$', user_views.pro_upgrade),
    re_path(r'^accounts/paid/$', user_views.pro_paid),
    re_path(r'^accounts/pro/thanks/$', user_views.pro_thanks),

    re_path(r'^signup/$', account_views.anti_spam),

    re_path(r'^acc/', include('django_registration.backends.activation.urls')),
]
