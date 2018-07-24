# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from bbr3.notification import notify
from users.models import PointsAward
from celery.task import task
from django.conf import settings
from django.core.mail import send_mail
import tweepy
from badges.models import Badge
from bands.models import Band
from badges.tasks import award_badge
from users.tasks import award_points_and_save

@task(ignore_result=True)
def notification(pThingOld, pThingNew, pObjectType, pChangeType, pUser, pBrowserDetails, pDestination=None, pAdditionalContext=None):
    """
    Send an admin notification email when something happens in bands module
    """
    if pObjectType == 'band' and pChangeType == 'edit':
        if _location_changed(pThingOld, pThingNew):
            lTweetContents = _tweet_band_move(pThingNew)
            _award_points_for_map_move(pThingNew, pUser, pBrowserDetails)
    
    elif pObjectType == 'band_map' and pChangeType == 'move':
        lTweetContents = _tweet_band_move(pThingNew)
        _award_points_for_map_move(pThingNew, pUser, pBrowserDetails)
        pAdditionalContext = {'TweetContents' : lTweetContents}
    
    notify(pThingOld = pThingOld, 
           pThingNew = pThingNew, 
           pModule = 'bands', 
           pObjectType = pObjectType, 
           pChangeType = pChangeType,
           pUser = pUser,
           pBrowserDetails = pBrowserDetails, 
           pDestination = pDestination,
           pAdditionalContext = pAdditionalContext)
    
    
def _award_points_for_map_move(pNewBand, pUser, pBrowserDetails):
    """
    Award reputation points to user for map move
    """
    if pNewBand.mapper != pUser:
        pNewBand.mapper = pUser
        pNewBand.save()
        award_points_and_save.delay(pUser, PointsAward.TYPE_BAND_MAPPER, pNewBand, 5, pBrowserDetails)
        
    award_badge.delay(pUser, Badge.CARTOGRAPHER)
    if Band.objects.filter(mapper=pUser).count() >= 10:
        award_badge.delay(pUser, Badge.MASTER_MAPPER)
    
    
def _location_changed(pOldBand, pNewBand):
    """
    Has the band location changed
    """
    lReturn = True
    if pOldBand.latitude == pNewBand.latitude and pOldBand.longitude == pNewBand.longitude:
        lReturn = False
    if pNewBand.latitude == '' or pNewBand.latitude == None:
        lReturn = False
    return lReturn

def _tweet_band_move(pNewBand):
    """
    Tweet that a band has been moved on the map
    """
    lMessage = "None"
    try:
        lAuth = tweepy.OAuthHandler(settings.TWEEPY_CONSUMER_TOKEN, settings.TWEEPY_CONSUMER_SECRET)
        lAuth.set_access_token(settings.TWEEPY_ACCESS_TOKEN_KEY, settings.TWEEPY_ACCESS_TOKEN_SECRET)
        lApi = tweepy.API(lAuth)
        lMessage = "%s moved on the map - https://brassbandresults.co.uk/map/band/%s/" % (pNewBand.name, pNewBand.slug)
        lApi.update_status(lMessage)
        return lMessage
    except Exception as inst:
        if str(inst) != "[{u'message': u'Status is a duplicate.', u'code': 187}]":
            lErrorMessage = "Problems Tweeting Map Move, %s %s\n\n%s" % (type(inst), str(inst), lMessage)
            send_mail('Error Tweeting', lErrorMessage, 'twitter@brassbandresults.co.uk', ['errors@brassbandresults.co.uk'], fail_silently=True)
            return lErrorMessage
        else:
            return "Twitter status is a duplicate"