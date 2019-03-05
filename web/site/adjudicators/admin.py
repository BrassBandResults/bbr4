# (c) 2009, 2012, 2015, 2017, 2018, 2019 Tim Sawyer, All Rights Reserved

from django.contrib import admin
from bbr.admin import BbrAdmin
from adjudicators.models import ContestAdjudicator

class ContestAdjudicatorAdmin(BbrAdmin):
    pass

admin.site.register(ContestAdjudicator, ContestAdjudicatorAdmin)
