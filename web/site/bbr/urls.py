# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

"""bbr4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from home import views as home_views
from accounts import views as account_views
from users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', home_views.home),
    url(r'^faq/$', home_views.faq),
    url(r'^aboutus/$', home_views.about),
    url(r'^privacy/$', home_views.cookies),

    url(r'^bbradmin/', admin.site.urls),

    url(r'^addresults/', include('addresults.urls')),
    url(r'^addwhitfriday/', include('addwhitfriday.urls')),
    url(r'^adjudicators/', include('adjudicators.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^badges/', include('badges.urls')),
    url(r'^bands/', include('bands.urls')),
    url(r'^calendar/', include('contest_calendar.urls')),
    url(r'^compare/', include('compare.urls')),
    url(r'^composers/', include('composers.urls')),
    url(r'^conductors/', include('conductors.urls')),
    url(r'^contests/', include('contests.urls')),
    url(r'^embed/', include('embed.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^feeds/', include('feeds.urls')),
    url(r'^leaderboard/', include('leaderboard.urls')),
    url(r'^map/', include('bandmap.urls')),
    url(r'^map2/', include('map2.urls')),
    url(r'^messages/', include('usermessages.urls')),
    url(r'^move/', include('move.urls')),
    url(r'^myresults/', include('myresults.urls')),
    url(r'^people/', include('people.urls')),
    url(r'^pieces/', include('pieces.urls')),
    url(r'^regions/', include('regions.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^sections/', include('sections.urls')),
    url(r'^statistics/', include('statistics.urls')),
    url(r'^tags/', include('tags.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^venues/', include('venues.urls')),
    url(r'^years/', include('years.urls')),
    
    url(r'^sitemap.xml$', home_views.sitemap_index),
    url(r'^robots.txt$', home_views.robotstxt),
    url(r'^ads.txt$', home_views.adstxt),

    url(r'^accounts/login/$', auth_views.login,  {'template_name': 'accounts/login.html'}),
    url(r'^accounts/logout/$', auth_views.logout,  {'template_name': 'accounts/logout.html'}),
    url(r'^accounts/forgottenpassword/$', user_views.forgotten_password),
    url(r'^accounts/forgottenpassword/sent/$', user_views.forgotten_password_sent),
    url(r'^accounts/resetpassword/([A-Za-z0-9]+)/$', user_views.reset_password),
    url(r'^accounts/changepassword/$', auth_views.password_change, {'template_name' : 'users/changepassword.html', 'post_change_redirect' : '/'}),

    url(r'^accounts/loginpro/$', auth_views.login, {'template_name' : 'accounts/loginpro.html',}),
    url(r'^accounts/upgrade/$', user_views.pro_upgrade),
    url(r'^accounts/paid/$', user_views.pro_paid),
    url(r'^accounts/pro/thanks/$', user_views.pro_thanks),

    url(r'^account/', include('registration.backends.hmac.urls')),
]
