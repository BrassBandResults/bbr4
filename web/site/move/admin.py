# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr.admin import BbrAdmin
from move.models import BandMergeRequest, VenueMergeRequest, PieceMergeRequest, PersonMergeRequest


class PersonMergeRequestAdmin(BbrAdmin):
    pass

class BandMergeRequestAdmin(BbrAdmin):
    pass

class VenueMergeRequestAdmin(BbrAdmin):
    pass

class PieceMergeRequestAdmin(BbrAdmin):
    pass


    
admin.site.register(PersonMergeRequest, PersonMergeRequestAdmin)
admin.site.register(BandMergeRequest, BandMergeRequestAdmin)
admin.site.register(VenueMergeRequest, VenueMergeRequestAdmin)
admin.site.register(PieceMergeRequest, PieceMergeRequestAdmin)
