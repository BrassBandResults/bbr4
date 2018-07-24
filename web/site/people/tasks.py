# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from celery.task import task
from bbr3.notification import notify

@task(ignore_result=True)
def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in people module
    """
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'people', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)