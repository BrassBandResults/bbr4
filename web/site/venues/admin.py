# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from contests.models import Venue
from bbr3.admin import BbrAdmin
from django.contrib import admin
from contests.models import VenueAlias

class VenueAliasInline(admin.TabularInline):
    model = VenueAlias

class VenueAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}
    list_display = ('name', 'country', 'exact', 'created', 'last_modified')
    list_filter = ('exact','country')
    inlines = [VenueAliasInline, ]
    
admin.site.register(Venue, VenueAdmin)    
