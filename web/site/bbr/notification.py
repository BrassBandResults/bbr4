# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

import boto3
from notification.notify import MessageWrapper
from django.conf import settings

def notification(pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None, pCc=None, pBcc=None, pFromName=None, pFromEmail=None):
    """
    Send an admin notification email when something happens
    """
    lMessage = MessageWrapper(pThingOld,
                              pThingNew,
                              pModule,
                              pObjectType,
                              pChangeType,
                              pUser,
                              pBrowserDetails,
                              pDestination,
                              pAdditionalContext,
                              pCc,
                              pBcc,
                              pFromName,
                              pFromEmail,  
                             )

    client = boto3.client('sns', region_name=settings.AWS_REGION)
    lMessage.send(client)
