# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from celery.task import task
from bbr3.notification import notify
from datetime import timedelta, date
from contests.models import ContestEvent
import tweepy
from django.conf import settings
from django.core.mail import send_mail
from users.models import PersonalContestHistoryDateRange, PointsAward, PersonalContestHistory
from badges.models import Badge
from badges.tasks import award_badge
from users.tasks import award_points_and_save
from bbr3.siteutils import shorten_url

@task(ignore_result=True)
def check_for_contest_history_badges(pContestResult, pUser):
    """
    Check to see if user needs awarding any badges, and award them if so
    """
    award_badge.delay(pUser, Badge.COMPETITOR) # user has a contest history
    lWins = PersonalContestHistory.objects.filter(user=pUser, result__results_position=1,status='accepted')
    if lWins.count() > 0:
        award_badge.delay(pUser, Badge.WON_CONTEST)
    

@task(ignore_result=True)
def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in contests module
    """
    if pObjectType == 'contestevent' and pChangeType == 'results_added': # new contest event with results added
        lTweetContents = _tweet_contest(pThingNew)
        pAdditionalContext = {'TweetContents' : lTweetContents}
        award_badge.delay(pUser, Badge.CONTRIBUTOR)
    
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'contests', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)
    
    if pObjectType == 'contest_result' and pChangeType == 'new':
        _check_for_contest_date_range_match(pUser, pThingNew, pBrowserDetails)
        award_points_and_save.delay(pUser, PointsAward.TYPE_CONTEST_RESULT, pThingNew, 1, pBrowserDetails)
    elif pObjectType == 'programme_cover' and pChangeType == 'new':
        _update_programme_on_events(pThingNew)
        award_badge.delay(pUser, Badge.PROGRAMME_SCANNER)
    elif pObjectType == 'future_event' and pChangeType == 'new':
        award_badge.delay(pUser, Badge.SCHEDULER)
        
        
def _check_for_contest_date_range_match(pUser, pContestResult, pBrowserDetails):
    """
    See if there are any users where this result matches their date range, and send an email to those who match
    """
    lContestEvent = pContestResult.contest_event
    lContext = {
                'ContestEvent' : lContestEvent,
                'ContestResult' : pContestResult,
                } 
    lNotifyDateRanges = PersonalContestHistoryDateRange.objects.filter(band=pContestResult.band, start_date__lte=lContestEvent.date_of_event, end_date__gte=lContestEvent.date_of_event)
    for daterange in lNotifyDateRanges:
        lContext.update({'DateRange' : daterange})
        notify(pThingOld = None,
               pThingNew = None, 
               pModule = 'contests', 
               pObjectType = 'contest_date_range', 
               pChangeType = 'match',
               pUser = pUser,
               pBrowserDetails = pBrowserDetails, 
               pDestination = daterange.user.email,
               pAdditionalContext = lContext)
        lPendingPersonalContestHistory = PersonalContestHistory()
        lPendingPersonalContestHistory.user = daterange.user 
        lPendingPersonalContestHistory.result = pContestResult
        lPendingPersonalContestHistory.status = 'pending'
        lPendingPersonalContestHistory.save()
                
    lOpenDateRanges = PersonalContestHistoryDateRange.objects.filter(band=pContestResult.band, start_date__lte=lContestEvent.date_of_event, end_date=None)
    for daterange in lOpenDateRanges:
        lContext.update({'DateRange' : daterange})
        notify(pThingOld = None,
               pThingNew = None, 
               pModule = 'contests', 
               pObjectType = 'contest_date_range', 
               pChangeType = 'match',
               pUser = pUser,
               pBrowserDetails = pBrowserDetails, 
               pDestination = daterange.user.email,
               pAdditionalContext = lContext)
        lPendingPersonalContestHistory = PersonalContestHistory()
        lPendingPersonalContestHistory.user = daterange.user 
        lPendingPersonalContestHistory.result = pContestResult
        lPendingPersonalContestHistory.status = 'pending'
        lPendingPersonalContestHistory.save()

       
def _update_programme_on_events(pProgrammeCover):
    """
    Assign the programme cover serial onto all existing events that it relates to
    """
    lDaysTolerance = 4
    lFewDaysAgo = pProgrammeCover.event_date - timedelta(days=lDaysTolerance)
    lFewDaysInFuture = pProgrammeCover.event_date + timedelta(days=lDaysTolerance)
    if pProgrammeCover.contest_id:
        ContestEvent.objects.filter(contest__id=pProgrammeCover.contest_id, date_of_event__gt=lFewDaysAgo, date_of_event__lt=lFewDaysInFuture).update(programme_cover=pProgrammeCover)
    else:
        ContestEvent.objects.filter(contest__group__id=pProgrammeCover.contest_group_id, date_of_event__gt=lFewDaysAgo, date_of_event__lt=lFewDaysInFuture).update(programme_cover=pProgrammeCover)
        
        
def _tweet_contest(pContestEvent):
    """
    Tweet that a new contest's results have been added
    """
    lMessage = "None"
    try:
        lUrl = "https://brassbandresults.co.uk%s" % pContestEvent.get_absolute_url()
        lShortUrl = shorten_url(lUrl).strip()
        lAuth = tweepy.OAuthHandler(settings.TWEEPY_CONSUMER_TOKEN, settings.TWEEPY_CONSUMER_SECRET)
        lAuth.set_access_token(settings.TWEEPY_ACCESS_TOKEN_KEY, settings.TWEEPY_ACCESS_TOKEN_SECRET)
        lApi = tweepy.API(lAuth)
        
        lWinner = None
        lFoundResult = False
        for result in pContestEvent.contestresult_set.all():
            if result.results_position > 0 and result.results_position < 1000:
                lFoundResult = True
                if result.results_position == 1:
                    lWinner = result
        
        lToday = date.today()
        lContestInFuture = pContestEvent.date_of_event > lToday
        if lContestInFuture:
            lMessage = "Bands added for %s (%s) %s" % (pContestEvent.contest.name, pContestEvent.event_date, lShortUrl)
        else:
            if lFoundResult:
                lMessage = "Results added for %s (%s) %s" % (pContestEvent.contest.name, pContestEvent.event_date, lShortUrl)
            else:
                lMessage = "Bands added for %s (%s) %s" % (pContestEvent.contest.name, pContestEvent.event_date, lShortUrl)
        if lWinner and lWinner.band.twitter_name and len(lWinner.band.twitter_name) > 0:
            lMessage += " @%s" % lWinner.band.twitter_name                
        if pContestEvent.hashtag:
            lMessage += " #%s" % pContestEvent.hashtag
        lApi.update_status(lMessage)
        return lMessage
    except Exception as inst:
        if str(inst) != "[{u'message': u'Status is a duplicate.', u'code': 187}]":
            lErrorMessage = "Problems Tweeting, %s\n\n%s\n\n%s" % (type(inst), str(inst), lMessage)
            send_mail('%s Error Tweeting' % settings.EMAIL_SUBJECT_PREFIX, lErrorMessage, 'twitter@brassbandresults.co.uk', ['errors@brassbandresults.co.uk'], fail_silently=True)
            return lErrorMessage
        else:
            return "Twitter status is a duplicate"
      
      
