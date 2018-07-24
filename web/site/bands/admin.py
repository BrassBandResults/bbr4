# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin
from bbr3.admin import BbrAdmin
from bands.models import Band, PreviousBandName, BandRelationship, BandTalkPage

class PreviousBandNameInline(admin.TabularInline):
    model = PreviousBandName

class BandAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}
    search_fields = ['name']
    inlines = [PreviousBandNameInline]
    
class BandRelationshipAdmin(BbrAdmin):
    search_fields = ['left_band__name', 'left_band_name','right_band__name', 'right_band_name']
    list_display = ('left_band', 'relationship', 'right_band', 'created', 'last_modified')
    
class BandTalkPageAdmin(BbrAdmin):
    pass

admin.site.register(Band, BandAdmin)
admin.site.register(BandRelationship, BandRelationshipAdmin)
admin.site.register(BandTalkPage, BandTalkPageAdmin)
