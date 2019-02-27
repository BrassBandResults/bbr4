# (c) 2009, 2012, 2015, 2017, 2019 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr.admin import BbrAdmin
from home.models import FaqSection, FaqEntry


class FaqSectionAdmin(BbrAdmin):
    pass

class FaqEntryAdmin(BbrAdmin):
    pass

admin.site.register(FaqSection, FaqSectionAdmin)
admin.site.register(FaqEntry, FaqEntryAdmin)
