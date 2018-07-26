# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin
from bbr.admin import BbrAdmin
from tags.models import ContestTag

class ContestTagAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}

admin.site.register(ContestTag, ContestTagAdmin)
