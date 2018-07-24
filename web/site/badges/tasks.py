# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from celery.task import task

from badges.models import Badge
from bbr3.notification import notify
from users.models import UserBadge


@task(ignore_result=True)
def award_badge(pUser, pBadgeSerial):
    """
    Award a badge to a user, if they don't already have it
    """
    if pUser == None:
        return
    lBadge = Badge.objects.filter(id=pBadgeSerial)[0]
    try:
        lExistingMatch = UserBadge.objects.filter(user=pUser, type__id=pBadgeSerial)[0]
        # they already have the badge
        return
    except IndexError:
        # don't have it - award it
        lNewUserBadge = UserBadge()
        lNewUserBadge.type = lBadge
        lNewUserBadge.user = pUser
        lNewUserBadge.save()
       
        notify(pThingOld = None, 
               pThingNew = lNewUserBadge, 
               pModule = 'badges', 
               pObjectType = "badge_award", 
               pChangeType = "new",
               pUser = pUser,
               pBrowserDetails = ('',''), 
              )
    