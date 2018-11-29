# (c) 2018 Tim Sawyer, All Rights Reserved

import os
import boto3
import json
import time
import psycopg2
from datetime import datetime

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


def addBadge(conn, badgeType, user_id):
  print("Adding %d badge to %s" % (badgeType, user_id))

  sql = "INSERT INTO users_userbadge (user_id, type_id, notified) values (%d, %d, false) ON CONFLICT DO NOTHING"
  cursor = conn.cursor()
  cursor.execute(sql, (user_id, badgeType))
  cursor.close()  
 

def lambda_handler(event, context):
  print(event)    
  print(event["Records"][0]["Sns"]["Message"])
  parsedMessage = json.loads(event["Records"][0]["Sns"]["Message"].replace('""','" "'))
  print (parsedMessage)
  
  notifyModule = parsedMessage["notification"]["module"]
  notifyType = parsedMessage["notification"]["type"]
  notifyChange = parsedMessage["notification"]["change"]

  userToAddTo = parsedMessage["notification"]["user"]

  notifyContextPath = "%s.%s.%s" % (notifyModule, notifyType, notifyChange)
  
  print("Looking for notification path %s" % notifyContextPath)

  if ('bands.band.edit' == notifyContextPath) and _moved(parsedMessage["notification"]):
    # band edited with location move, so make sure to add points
    notifyContextPath = 'bands.band_map.move'  
 
  if ('venues.venue.edit' == notifyContextPath) and _moved(parsedMessage["notification"]):
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
    db_connect_string = os.environ['BBR_DB_CONNECT_STRING']
    print ("Connect to database")
    conn = psycopg2.connect(db_connect_string)
    print ("Connected")

    user_id = None
    cursor = conn.cursor()
    selectUserSql = "SELECT id FROM auth_user WHERE username = %s"
    cursor.execute(selectUserSql, (userToAddTo,))
    rows = cursor.fetchall()
    for row in rows:
      user_id = row[0]
    cursor.close()
  
    print("User id for %s is %s" % (userToAddTo, user_id))


  if badgeToAdd:
    addBadge(conn, bandToAdd, user_id)


  oldPointsLog = 0
  newPointsLog = 0

  if pointsToAdd:
    print("Adding %d points to %s" % (pointsToAdd, userToAddTo))

    old_points = -100
    selectPointsSql = "SELECT points FROM users_userprofile WHERE user_id = %s FOR UPDATE"
    cursor = conn.cursor() 
    cursor.execute(selectPointsSql, (user_id,))
    rows = cursor.fetchall()
    for row in rows:
      old_points = row[0]
    cursor.close()

    new_points = old_points + pointsToAdd
    print("Old points %d, New Points %d" % (old_points, new_points))

    oldPointsLog = old_points
    newPointsLog = new_points

    if (old_points >= 0):
    	updatePointsSql = "UPDATE users_userprofile SET points = %s WHERE user_id = %s"
    	cursor = conn.cursor()
    	cursor.execute(updatePointsSql, (new_points, user_id))
    	cursor.close()   

    	print ("Points updated")
    else:
        print ("User id %d not found" % user_id)

  if badgeToAdd or pointsToAdd:
    conn.commit()
    conn.close()

    print ("Done")

  # Write to event log
  print ("Connecting to DynamoDB")
  dynamodb = boto3.resource('dynamodb')
  event_table = dynamodb.Table("EventLog")
  print ("Obtained reference to table")

  lNowString = str(datetime.now())
  lNowNumber = int(round(time.time()))
  lExpiryTimeNumber = lNowNumber + 2764800 # 32 days

  dataToStore = {
             'Username' : userToAddTo,
             'DateTimestamp' : lNowNumber,
             'DateTime' : lNowString,
             'EventType' : notifyContextPath,
             'Points' : pointsToAdd,
             'OldPoints' : oldPointsLog,
             'NewPoints' : newPointsLog,
             'Data' : parsedMessage["notification"],
             'TimeToLive' : lExpiryTimeNumber
           }
  print(dataToStore)

  print ("Writing...")
  response = event_table.put_item(Item = dataToStore)
  print("Log written to event table")

