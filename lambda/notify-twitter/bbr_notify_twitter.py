import json
import tweepy


def _tweet_ContestResults(notification):
  """
  Tweet out when contest results have changed
  """
  contestEvent = notification["ThingNew"]
  contestName = contestEvent.name
  contestEventDate = contestEvent.date_of_event
  contestEventUrl = "http://"
  return "%s (%s) Updated %s %s" % (contestName, contestEventDate, contestEventUrl, winnersTwitter)
    

def _tweet_BandMapMove(notification):
  """
  Tweet out when a band is moved on the map
  """
  bandMoved = notification["ThingNew"]
  bandName = bandMoved.name
  bandUrl = "https://brassbandresults.co.uk/map/band/%s/" % bandMoved.slug
  return "%s moved on map %s" % (bandName, bandUrl)


TWITTER_TEMPLATES = {
  "contests.contestevent.results_added" : _tweet_ContestResults, 
  "bands.band_map.move" : _tweet_BandMapMove,
}


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
    pass
  
  if tweetFunction:
    messageToTweet = tweetFunction(parsedMessage["notification"])
    print("Tweeting %s" % messageToTweet)