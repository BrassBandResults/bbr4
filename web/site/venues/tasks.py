# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from celery.task import task
from bbr3.notification import notify
from users.models import PointsAward
from badges.models import Badge
from badges.tasks import award_badge
from contests.models import Venue
from users.tasks import award_points_and_save

@task(ignore_result=True)
def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails):
    """
    Send an admin notification email when something happens in venues module
    """
    if pObjectType == 'venue' and pChangeType == 'edit':
        if _location_changed(pThingOld, pThingNew):
            _award_points_for_map_move(pThingNew, pUser, pBrowserDetails)
    
    notify(pThingOld, pThingNew, 'venues', pObjectType, pChangeType, pUser, pBrowserDetails)
    
    
def _award_points_for_map_move(pNewVenue, pUser, pBrowserDetails):
    """
    Award reputation points to user for map move
    """
    if pNewVenue.mapper != pUser:
        award_points_and_save.delay(pUser, PointsAward.TYPE_VENUE_MAPPER, pNewVenue, 5, pBrowserDetails)
        lNewVenue = Venue.objects.filter(id=pNewVenue.id)[0]
        lNewVenue.mapper = pUser
        lNewVenue.save()
    award_badge.delay(pUser, Badge.VENUE_CARTOGRAPHER)
    
def _location_changed(pOldVenue, pNewVenue):
    """
    Has the venue location changed
    """
    lReturn = True
    if pOldVenue.latitude == pNewVenue.latitude and pOldVenue.longitude == pNewVenue.longitude:
        lReturn = False
    if pNewVenue.latitude == '' or pNewVenue.latitude == None:
        lReturn = False
    return lReturn