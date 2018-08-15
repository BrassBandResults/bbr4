# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

import boto3
from django.conf import settings
from django.core import serializers
from django.template.loader import render_to_string

from notification.notify import MessageWrapper


def notification(pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None, pCc=None, pBcc=None, pFromName=None, pFromEmail=None):
    """
    Send an admin notification email when something happens
    """
    if settings.NOTIFICATIONS_ENABLED == False:
        # disable all notifications for testing purposes
        return

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
