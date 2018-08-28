# (c) 2018 Tim Sawyer, All Rights Reserved

import os
import json
import tweepy
from dateutil.parser import parse


def _tweet_ContestResults(notification):
  """
  Tweet out when contest results have changed
  """
  contestEvent = notification["thingNew"][0]["fields"]
  contestName = contestEvent["name"]
  contestEventDateRaw = contestEvent["date_of_event"]
  contestEventDateParsed = parse(contestEventDateRaw)
  contestEventDate = strftime("%a, %-d %b, %Y")
  contestEventUrl = "https://brassbandresults.co.uk%s" % notification["url"]
  winnersTwitter = notification["_WinnersTwitter"]
  return "%s on %s updated: %s %s" % (contestName, contestEventDate, contestEventUrl, winnersTwitter)
    

def _tweet_BandMapMove(notification):
  """
  Tweet out when a band is moved on the map
  """
  bandMoved = notification["thingNew"][0]["fields"]
  bandName = bandMoved["name"]
  bandUrl = "https://brassbandresults.co.uk/map/band/%s/" % bandMoved.slug
  bandTwitter = bandMoved["twitter_name"]
  if bandTwitter:
    bandTwitter = "@" + bandTwitter
  else:
    bandTwitter = ""
  return "%s moved on map %s %s" % (bandName, bandUrl, bandTwitter)


TWITTER_TEMPLATES = {
  "contests.contestevent.results_added" : _tweet_ContestResults, 
  "bands.band_map.move" : _tweet_BandMapMove,
}

def _tweet(message):
  """
  Post message to twitter
  """
  try:
    lAuth = tweepy.OAuthHandler(os.environ['TWEEPY_CONSUMER_TOKEN'], os.environ['TWEEPY_CONSUMER_SECRET'])
    lAuth.set_access_token(os.environ['TWEEPY_ACCESS_TOKEN_KEY'], os.environ['TWEEPY_ACCESS_TOKEN_SECRET'])
    lApi = tweepy.API(lAuth)
    lApi.update_status(message)
  except Exception as inst:
    print (str(inst))
    if str(inst) != "[{u'message': u'Status is a duplicate.', u'code': 187}]":
      print ("Status is duplicate")
      #send_mail('Error Tweeting', lErrorMessage, 'twitter@brassbandresults.co.uk', ['errors@brassbandresults.co.uk'], fail_silently=True)

def lambda_handler(event, context):
  print(event)    
  print(event["Records"][0]["Sns"]["Message"])
  parsedMessage = json.loads(event["Records"][0]["Sns"]["Message"])
  print (parsedMessage)
  
  notifyModule = parsedMessage["notification"]["module"]
  notifyType = parsedMessage["notification"]["type"]
  notifyChange = parsedMessage["notification"]["change"]

  notifyContextPath = "%s.%s.%s" % (notifyModule, notifyType, notifyChange)
  
  print("Looking for notification path %s" % notifyContextPath)
  
  tweetFunction = None
  try:
    tweetFunction = TWITTER_TEMPLATES[notifyContextPath]
  except KeyError:
    print ("No matching tweet template found")
  
  if tweetFunction:
    messageToTweet = tweetFunction(parsedMessage["notification"])
    print("Tweeting %s" % messageToTweet)

    _tweet(messageToTweet)