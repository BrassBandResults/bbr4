# (c) 2018 Tim Sawyer, All Rights Reserved

import os
import json
import psycopg2
import boto3

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

  email_subject = parsedMessage["notification"]["subject"]
  email_text = parsedMessage["notification"]["message"]

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

    ses_client = boto3.client('ses',region_name='eu-west-1')
    response = ses_client.send_email(
      Source='contact@brassbandresults.co.uk',
      Destination={
        'ToAddresses': [email_address,],
        'CcAddresses': [],
        'BccAddresses': ['maillog@brassbandresults.co.uk',],
      },
      Message={
        'Subject': {
          'Data' : email_subject,
          'Charset': 'UTF-8',
        },
        'Body' : {
          'Text': {
            'Charset' : 'UTF-8',
            'Data' : email_text,
          }
        },
      }
    )
    
  cursor.close()

  conn.close()
