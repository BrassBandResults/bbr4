# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from bbr.notification import notify
from users.models import PointsAward 
from users.tasks import award_points_and_save



def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in feedback module
    """
    if pObjectType == 'feedback' and pChangeType == 'claim':
        award_points_and_save(pUser, PointsAward.TYPE_FEEDBACK_CLAIM, pThingNew, 5, pBrowserDetails)
    
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'feedback', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)
    
    
    
    