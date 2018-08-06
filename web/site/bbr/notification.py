# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

import boto3
from django.conf import settings

class MessageWrapper:
    """
    Wrapper for SNS message, used to convert parameter through to JSON
    """
    thingOld = None
    thingNew = None
    module = None
    objectType = None
    changeType = None
    user = None
    browserDetails = None
    destination = None
    additionalContext = None
    cc = None
    bcc = None
    fromName = None
    fromEmail = None

    def __init__(self, pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination, pAdditionalContext, pCc, pBcc, pFromName, pFromEmail):
        self.thingOld = pThingOld
        self.thingNew = pThingNew
        self.module = pModule
        self.objectType = pObjectType
        self.changeType = pChangeType
        self.user = pUser
        self.browserDetails = pBrowserDetails
        self.destination = pDestination
        self.additionalContext = pAdditionalContext
        self.cc = pCc
        self.bcc = pBcc
        self.fromName = pFromName
        self.fromEmail = pFromEmail

    def asJson(self):
        return "{'json': 'json'}"


def notify(pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None, pCc=None, pBcc=None, pFromName=None, pFromEmail=None):
    """
    Send an admin notification email when something happens
    """
    if settings.NOTIFICATIONS_ENABLED == false:
        # disable all notifications for tesitng purposes
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

    client = boto3.client('sns')
    client.publish(
            TopicArn = settings.NOTIFICATION_TOPIC_ARN,
            Message = lMessage.asJson(),
        )
