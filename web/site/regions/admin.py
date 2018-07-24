# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin
from bbr3.admin import BbrAdmin
from regions.models import Region

class RegionAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}

admin.site.register(Region, RegionAdmin)