# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from celery.task import task
from bbr3.notification import notify
import difflib
import textwrap

@task(ignore_result=True)
def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in classifieds module
    """
    if (pObjectType == 'profile' or pObjectType == 'band_profile') and pChangeType == 'edit':
        lOldProfile = textwrap.wrap(pThingOld.profile, 80)
        lNewProfile = textwrap.wrap(pThingNew.profile, 80)
        
        lDiff = difflib.Differ()
        lProfileDiffLines = lDiff.compare(lOldProfile, lNewProfile)
        lProfileDiff = '\n'.join(list(lProfileDiffLines))
        if pAdditionalContext == None:
            pAdditionalContext = {}
        pAdditionalContext.update({'ProfileDiff' : lProfileDiff})
    
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'classifieds', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)
        

       
