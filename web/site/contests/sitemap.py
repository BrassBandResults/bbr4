# -*- coding: utf-8 -*-
# (c) 2012 Tim Sawyer, All Rights Reserved

from django.contrib.sitemaps import Sitemap
from contests.models import Contest

class ContestSitemap(Sitemap):
    changefreq="weekly"
    priority="0.6"
    
    def items(self):
        return Contest.objects.all().select_related()
    
    def lastmod(self, obj):
        try:
            return obj.contestevent_set.all().order_by('-id')[0].last_modified
        except IndexError:
            return None