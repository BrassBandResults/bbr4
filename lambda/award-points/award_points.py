# (c) 2018 Tim Sawyer, All Rights Reserved

import boto3
import json


POINTS = {
  # New result 1 point
  # Map move 5 points
  # Feedback claim 5 points
  # Venue map 5 points
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
  
  pointsToAdd = 0
  try:
    pointsToAdd  = POINTS[notifyContextPath]
  except KeyError:
    pass 
  if pointsToAdd:
    print("Adding %s points to user %s" % (pointsToAdd, userToAddTo))

