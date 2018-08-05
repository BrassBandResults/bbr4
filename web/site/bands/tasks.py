# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

from bbr.notification import notify


def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in bands module
    """
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'bands', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)
