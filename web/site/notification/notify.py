# (c) 2018 Tim Sawyer, All Rights Reserved
from django.core import serializers
from django.conf import settings
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

    def send(self, client):
        """
        Send message
        """
        lMessageToSend = self.asJson()
        client.publish(
            TopicArn = settings.NOTIFICATION_TOPIC_ARN,
            Message = lMessageToSend,
        )

    def asJson(self):
        """
        Convert message to JSON
        """
        lContext = {
          'module' : self.module,
          'objectType' : self.objectType,
          'change' : self.changeType,
          'user' : self.user,
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
        if self.browserDetails:
          lContext['ip']  =  self.browserDetails[0]
          lContext['browser'] = self.browserDetails[1]

        lRenderedString = render_to_string('notify/message.json', lContext)
        return lRenderedString