# (c) 2018 Tim Sawyer, All Rights Reserved
from django.core import serializers
from django.conf import settings
from django.template.loader import render_to_string
import json

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
    url = None

    def __init__(self, pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination, pAdditionalContext, pCc, pBcc, pFromName, pFromEmail, pUrl):
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
        self.url = pUrl

    def send(self, client):
        """
        Send message
        """
        lMessageToSend, lSubjectToSend = self.asJson()
        if settings.NOTIFICATIONS_ENABLED == True:
          client.publish(
            TopicArn = settings.NOTIFICATION_TOPIC_ARN,
            Message = lMessageToSend,
            Subject = lSubjectToSend,
            MessageStructure = "json",
          )
        else:
          print (lSubjectToSend)
          print (lMessageToSend)  
          json.loads(lMessageToSend)

    def asJson(self):
        """
        Convert message to JSON
        """
        lContext = {
          'Module' : self.module,
          'ObjectType' : self.objectType,
          'Change' : self.changeType,
          'User' : self.user,
          'Destination': self.destination,
          'Cc': self.cc,
          'Bcc': self.bcc,
          'FromName': self.fromName,
          'FromEmail': self.fromEmail,
          'ThingOld': self.thingOld,
          'ThingNew': self.thingNew,
          'AdditionalContext' : self.additionalContext,
          'Url' : self.url,
        }

        if self.thingOld:
          lThingOldJson = serializers.serialize("json", [self.thingOld,])
          lContext['ThingOldJson'] = '\\n'.join(lThingOldJson.splitlines()) #  *must not* contain newlines
        if self.thingNew:
          lThingNewJson = serializers.serialize("json", [self.thingNew,])
          lContext['ThingNewJson'] = '\\n'.join(lThingNewJson.splitlines()) #  *must not* contain newlines
        if self.browserDetails:
          lContext['Ip']  =  self.browserDetails[0]
          lContext['Browser'] = self.browserDetails[1]

        lRenderedEmail = render_to_string('%s/notify/%s_%s.txt' % (self.module, self.changeType, self.objectType), lContext)
        lRenderedEmailText = '\\n'.join(lRenderedEmail.splitlines()) #  *must not* contain newlines
        lContext['Message'] = '!NEW_LINE!'.join(lRenderedEmail.splitlines()) #  *must not* contain newlines
         
        lRenderedEmailSubject = render_to_string('%s/notify/%s_%s_subject.txt' % (self.module, self.changeType, self.objectType), lContext)
        lRenderedEmailSubject = ''.join(lRenderedEmailSubject.splitlines()) #  *must not* contain newlines
        lContext['Subject'] = lRenderedEmailSubject

        lRenderedJsonText = render_to_string('notify/default_message.json', lContext)
        lRenderedJsonText = ''.join(lRenderedJsonText.splitlines()) #  *must not* contain newlines
        
        lSnsContext = {
          'emailText' : lRenderedEmailText,
          'jsonText' : lRenderedJsonText.replace('"','\\"')
        }
        lRenderedJson = render_to_string('notify/sns_message.json', lSnsContext)
        return lRenderedJson, lRenderedEmailSubject