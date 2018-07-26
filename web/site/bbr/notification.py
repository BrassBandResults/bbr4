# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from audit.models import AuditEntry
from bbr.siteutils import shorten_url
from users.models import UserNotification
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string, TemplateDoesNotExist
import tweepy

def _tweet(pTweetMessage):
    """
    Tweet the specified message
    """
    try:
        lAuth = tweepy.OAuthHandler(settings.TWEEPY_CONSUMER_TOKEN, settings.TWEEPY_CONSUMER_SECRET)
        lAuth.set_access_token(settings.TWEEPY_ACCESS_TOKEN_KEY, settings.TWEEPY_ACCESS_TOKEN_SECRET)
        lApi = tweepy.API(lAuth)
        lTweet = ''.join(pTweetMessage.splitlines()) # Remove newlines
        
        # shorten urls if there are any
        if lTweet.find('http://') > -1:
            lUrlStart = lTweet.find('http://')
            lUrlEnd = lTweet[lUrlStart:].find(' ') + lUrlStart
            lUrl = lTweet[lUrlStart:lUrlEnd]
            lNewUrl = shorten_url(lUrl)
            lTweet = lTweet[:lUrlStart] + lNewUrl + lTweet[lUrlEnd:]
        
        # make sure under 140 chars
        if len(lTweet) > 140: 
            lTweet = "%s..." % lTweet[0:136]
        lApi.update_status(lTweet)
    except Exception as inst:
        if str(inst) != "[{u'message': u'Status is a duplicate.', u'code': 187}]":
            lErrorMessage = "Problems Tweeting, %s %s\n\n%s\n\n%s" % (type(inst), inst.reason, str(inst), lTweet)
            send_mail('Error Tweeting', lErrorMessage, 'twitter@brassbandresults.co.uk', ['errors@brassbandresults.co.uk'], fail_silently=True)


def notify(pThingOld, pThingNew, pModule, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None, pCc=None, pBcc=None, pFromName=None, pFromEmail=None):
    """
    Send an admin notification email when something happens
    """
    if settings.NOTIFICATIONS_ENABLED = false:
        # disable all notifications for tesitng purposes
        return

    lContext = { 'ThingNew'  : pThingNew,
                 'ThingOld'  : pThingOld,
                 'User'      : pUser,
                }
    if pAdditionalContext:
        lContext.update(pAdditionalContext)
    
    lSubject = render_to_string('%s/notify/%s_%s_subject.txt' % (pModule, pChangeType, pObjectType), lContext)
    lSubject = ''.join(lSubject.splitlines()) # Email subject *must not* contain newlines

    lMessage = render_to_string('%s/notify/%s_%s.txt' % (pModule, pChangeType, pObjectType), lContext)
    
    try:
        lTweet = render_to_string('%s/notify/%s_%s.twitter' % (pModule, pChangeType, pObjectType), lContext)
        _tweet(lTweet)
    except TemplateDoesNotExist:
        pass
    
    if pDestination:
        lDestinations = [pDestination,]
    else:
        lDestinations = []
                    
    if pFromName:
        lFrom = '%s <%s@brassbandresults.co.uk>' % (pFromName, pChangeType)
        if pFromEmail:
            lFrom = '%s <%s>' % (pFromName, pFromEmail)
    else:
        lFrom = 'BrassBandResults <%s@brassbandresults.co.uk>' % pChangeType
        
    lMessageType = "%s_%s" % (pChangeType, pObjectType)
    lUserNotifications = UserNotification.objects.filter(type=lMessageType, enabled=True)
    for lUserNotification in lUserNotifications:
        if lUserNotification.notify_user.profile.new_email_required:
            continue # user email doesn't work, no point notifying
        lEmailToAdd = None
        
        if hasattr(pThingNew, 'owner') and pThingNew.owner == lUserNotification.notify_user:
            # You are the owner
            if lUserNotification.notify_type == 'own' or lUserNotification.notify_type == 'all':
                lEmailToAdd = lUserNotification.notify_user.email
            elif lUserNotification.notify_type == 'notown' and pUser != pThingNew.owner:
                lEmailToAdd = lUserNotification.notify_user.email
        else:
            # You are not the owner
            if lUserNotification.notify_type == 'all':
                lEmailToAdd = lUserNotification.notify_user.email
             
        if lUserNotification.name_match:
            # a name match has been specified
            if lUserNotification.name_match.find(',') > -1:
                # it's multiple words separated by commas
                lNameMatches = lUserNotification.name_match.split(',')
            else:
                lNameMatches = (lUserNotification.name_match,)
            lFoundOne = False
            for lNameMatch in lNameMatches:
                try:
                    # if any of the words are found in the name of the contest, we've got a match
                    if pThingNew.name.lower().find(lNameMatch.strip().lower()) > -1:
                        lFoundOne = True
                except AttributeError:
                    pass
            
            # We have a name match specified, but we didn't find any of the words
            if lFoundOne == False:
                lEmailToAdd = None
   
        if lEmailToAdd:
            lDestinations.append(lEmailToAdd)
    
    lCc = []
    if pCc != None:
        lCc.extend(pCc)
    
    lBcc = []
    if pBcc != None:
        lBcc.extend(pBcc) 
        
    for destination in lDestinations:
        lMessageToSend = lMessage
        lNewSubject = lSubject
        if destination.endswith('brassbandresults.co.uk'):
            lCc = []
            lBcc = []
            
            lMessageToSend = "%s\n\n%s\n" % (lMessage, pUser.username)
            lNewSubject = "%s %s" % (settings.EMAIL_SUBJECT_PREFIX, lSubject) 
        
        lEmailMessage = EmailMessage(subject=lNewSubject,
                            body=lMessageToSend,
                            from_email=lFrom,
                            to=[destination],
                            cc=lCc,
                            bcc=lBcc)
        lEmailMessage.send(True)
        
    lAuditEntry = AuditEntry()
    lAuditEntry.subject = lSubject
    lAuditEntry.module = pModule
    lAuditEntry.object_type = pObjectType
    lAuditEntry.change_type = pChangeType
    lAuditEntry.message = lMessage
    if pUser.is_anonymous() == False:
        lAuditEntry.user = pUser
    lAuditEntry.useragent = pBrowserDetails[1]
    lAuditEntry.address = pBrowserDetails[0] 
    lAuditEntry.save()        