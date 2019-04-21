# (c) 2018 Tim Sawyer, All Rights Reserved
from django.core import serializers
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User

import logging
import os
import boto3
import json
import time

from datetime import datetime

from badges.models import Badge
from users.models import UserProfile, UserBadge

WON_CONTEST = 1
BAND_CARTOGRAPHER = 9
MASTER_MAPPER = 10
COMPETITOR = 12
CONTRIBUTOR = 13
VENUE_CARTOGRAPHER = 11
PROGRAMME_SCANNER = 14
SCHEDULER = 15

BADGES = {
  "venues.venue_map.move" : VENUE_CARTOGRAPHER,
  "bands.band_map.move" : BAND_CARTOGRAPHER,
  # : MASTER_MAPPER,
  "contests.performances.new" : COMPETITOR,
  "contests.performances.accept" : COMPETITOR,
  # : WON_CONTEST,
  "contests.contestevent.results_added" : CONTRIBUTOR,
  "contests.programme_cover.new" : PROGRAMME_SCANNER,
  "contests.future_event.new" : SCHEDULER,
}


POINTS = {
  "contests.contest_result.new" : 1,
  "feedback.feedback.claim" : 5,
  "feedback.feedback.to_queue": -5,
  "venues.venue_map.move" : 5,
  "bands.band_map.move" : 5,
}


def addBadge(badgeType, user):
    # does this user already have this badge?
    lBadge = Badge.objects.filter(id=badgeType)[0]

    lBadgeCount = UserBadge.objects.filter(user=user, type=lBadge).count()
    if lBadgeCount == 0:
        print("Adding %d badge to %s" % (badgeType, user))
        lNewBadge = UserBadge()
        lNewBadge.user = user
        lNewBadge.type = lBadge
        lNewBadge.save()


def moved(messageWrapper):
    """
    Is ThingNew/ThingOld a band and has it moved
    """
    if messageWrapper.thingOld == None or messageWrapper.thingNew == None:
        return False

    isLocationChanged = False
    if messageWrapper.thingOld.latitude != messageWrapper.thingNew.latitude:
      isLocationChanged = True
    if messageWrapper.thingOld.longitude != messageWrapper.thingNew.longitude:
      isLocationChanged = True

    return isLocationChanged


def awardPointsAndBadges(messageWrapper):
    """
    Add appropriate points to appropriate user
    """
    notifyContextPath = "%s.%s.%s" % (messageWrapper.module, messageWrapper.objectType, messageWrapper.changeType)
    print("NOTIFICATION: %s" % notifyContextPath)
    userToAddTo = messageWrapper.user


    if ('bands.band.edit' == notifyContextPath) and moved(messageWrapper):
      # band edited with location move, so make sure to add points
      notifyContextPath = 'bands.band_map.move'

    if ('venues.venue.edit' == notifyContextPath) and moved(messageWrapper):
      # venue edited with location move
      notifyContextPath = "venues.venue_map.move"

    try:
      badgeToAdd = BADGES[notifyContextPath]
    except:
      badgeToAdd = None

    try:
      pointsToAdd  = POINTS[notifyContextPath]
    except KeyError:
      pointsToAdd = 0

    if badgeToAdd or pointsToAdd:
      lUserToAddTo = User.objects.filter(username=userToAddTo)[0]

    if badgeToAdd:
      addBadge(badgeToAdd, lUserToAddTo)

    if pointsToAdd:
      print("Adding %d points to %s" % (pointsToAdd, userToAddTo))

      lUserProfile = UserProfile.objects.filter(user__username=userToAddTo)[0]
      lUserProfile.points += pointsToAdd
      lUserProfile.save()


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
        print (lMessageToSend)

        awardPointsAndBadges(self)

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
          self.thingOld.notes = ""
          lThingOldJson = serializers.serialize("json", [self.thingOld,])
          lThingOldJson = lThingOldJson.replace('\t', '  ')
          lContext['ThingOldJson'] = '!NEW_LINE!'.join(lThingOldJson.splitlines()) #  *must not* contain newlines
        if self.thingNew:
          self.thingNew.notes = ""
          lThingNewJson = serializers.serialize("json", [self.thingNew,])
          lThingNewJson = lThingNewJson.replace('\t', '  ')
          lContext['ThingNewJson'] = '!NEW_LINE!'.join(lThingNewJson.splitlines()) #  *must not* contain newlines
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
