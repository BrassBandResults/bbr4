# (c) 2018 Tim Sawyer, All Rights Reserved

import os
import json
import psycopg2

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

  db_connect_string = os.environ['BBR_DB_CONNECT_STRING']
  print ("Connect to database")
  conn = psycopg2.connect(db_connect_string)
  print ("Connected")

  sql = """SELECT u.email, n.notify_type, n.name_match 
           FROM users_usernotification n
	   INNER JOIN auth_user u ON (n.notify_user_id = u.id)
           WHERE n.enabled = true
           AND u.is_active = true 
           AND n.type = %s"""

  cursor = conn.cursor()
  cursor.execute(sql, (notifyContextPath,))
  rows = cursor.fetchall()
  for row in rows:
    email_address = row[0]
    notify_type = row[1]
    name_match = row[2]

    print ("Sending email to %s for notification %s" % (email_address, notifyContextPath))
  cursor.close()

  conn.close()
