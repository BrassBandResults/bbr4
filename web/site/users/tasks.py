# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved


from bbr.notification import notify


def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in users module
    """
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'users', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)
    
    

def award_points_and_save(pUser, pAwardType, pAwardedFor, pNumberOfPoints, pBrowserDetails):
    """
    Award the specified number of points to the specified user, and send notification mail if over 100 points
    """
    lProfile = pUser.profile
    lPointsBefore = lProfile.points
    if pAwardedFor != None:
        lProfile.award_points_and_save(pAwardType, pAwardedFor.id, pNumberOfPoints)
    lPointsAfter = lProfile.points
    if lPointsBefore < 100 and lPointsAfter >= 100:
        notification(None, lProfile, 'reputation', 'enhanced', pUser, pBrowserDetails)