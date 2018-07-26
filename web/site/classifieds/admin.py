# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin
from bbr.admin import BbrAdmin
from classifieds.models import PlayerPosition
    
class PlayerPositionAdmin(BbrAdmin):
    pass

admin.site.register(PlayerPosition, PlayerPositionAdmin)