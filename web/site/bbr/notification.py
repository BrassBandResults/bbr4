# (c) 2009, 2012, 2015, 2017, 2018 Tim Sawyer, All Rights Reserved

import boto3
from django.conf import settings
from django.core import serializers
from django.template.loader import render_to_string

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
        lContext = {
          'module' : self.module,
          'objectType' : self.objectType,
          'change' : self.changeType,
          'user' : self.user,
          'ip': self.browserDetails[0], 
          'browser': self.browserDetails[1],
          'destination': self.destination,
          'cc': self.cc,
          'bcc': self.bcc,
          'fromName': self.fromName,
          'fromEmail': self.fromEmail,
          'ThingOld': 'null',
          'ThingNew': 'null',
        }

        if self.thingOld:
          lContext['ThingOld'] = serializers.serialize("json", [self.thingOld,])
        if self.thingNew:
          lContext['ThingNew'] = serializers.serialize("json", [self.thingNew,])

        lRenderedString = render_to_string('notify/message.json', lContext)
        return lRenderedString


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

    lMessageToSend = lMessage.asJson()
    if len(lMessageToSend) < 5:
      lMessageToSend = '{ "error": "INVALID MESSAGE", "message": "[%s]}"' % lMessageToSend
    client = boto3.client('sns', region_name=settings.AWS_REGION)
    client.publish(
            TopicArn = settings.NOTIFICATION_TOPIC_ARN,
            Message = lMessageToSend,
        )
