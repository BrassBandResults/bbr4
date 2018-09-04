# (c) 2018 Tim Sawyer, All Rights Reserved

import boto3
import json

def _moved(notification):
  """
  Return true if location of band in ThingNew differs from the one in ThingOld.
  """
  thingOld = notification["thingOld"][0]["fields"]
  thingNew = notification["thingNew"][0]["fields"]

  isLocationChanged = False
  if (thingOld["latitude"] != thingNew["latitude"]):
    isLocationChanged = True
  if (thingOld["longitude"] != thingNew["longitude"]):
    isLocationChanged = True

  return isLocationChanged


POINTS = {
  # New result 1 point
  "feedback.feedback.claim" : 5,
  "feedback.feedback.to_queue": -5,
  "venues.venue_map.move" : 5,
  "bands.band_map.move" : 5,
}


def lambda_handler(event, context):
  print(event)    
  print(event["Records"][0]["Sns"]["Message"])
  parsedMessage = json.loads(event["Records"][0]["Sns"]["Message"])
  print (parsedMessage)
  
  notifyModule = parsedMessage["notification"]["module"]
  notifyType = parsedMessage["notification"]["type"]
  notifyChange = parsedMessage["notification"]["change"]

  userToAddTo = parsedMessage["notification"]["user"]

  notifyContextPath = "%s.%s.%s" % (notifyModule, notifyType, notifyChange)
  
  print("Looking for notification path %s" % notifyContextPath)

  if ('bands.band.edit' == notifyContextPath && _moved(parsedMessage["notification"])):
    # band edited with location move, so make sure to add points
    notifyContextPath = 'bands.band_map.move'  
 
  if ('venues.venue.edit' == notifyContextPath && _moved(parsedMessage["notification"])):
    # venue edited with location move
    notifyContextPath = "venues.venue_map.move'
 
  try:
    pointsToAdd  = POINTS[notifyContextPath]
  except KeyError:
    pointsToAdd = 0 
  
if pointsToAdd:
    print("Adding %s points to user %s" % (pointsToAdd, userToAddTo))

