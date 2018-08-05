# (c) 2009, 2012, 2015, 2018 Tim Sawyer, All Rights Reserved
from bbr.notification import notify



def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails):
    """
    Send an admin notification email when something happens in venues module
    """
    notify(pThingOld, pThingNew, 'venues', pObjectType, pChangeType, pUser, pBrowserDetails)
    
  