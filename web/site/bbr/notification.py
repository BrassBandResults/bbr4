# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

def notify(pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None, pCc=None, pBcc=None, pFromName=None, pFromEmail=None):
    """
    Send an admin notification email when something happens
    """
    if settings.NOTIFICATIONS_ENABLED == false:
        # disable all notifications for tesitng purposes
        return