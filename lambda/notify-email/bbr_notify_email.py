# (c) 2018 Tim Sawyer, All Rights Reserved

import os
import json
import psycopg2
import boto3

def send_email(email_address, notifyContextPath, email_subject, email_text):
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

AUTO_SEND = {
'users.password_reset.request' : True,
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

  email_subject = parsedMessage["notification"]["subject"]
  email_text = parsedMessage["notification"]["message"]
  try:
    email_address = parsedMessage["notification"]["thingOld"][0]["fields"]["email"]
  except KeyError:
    email_address = None

  try:
    auto_send = AUTO_SEND[notifyContextPath]
  except KeyError:
    auto_send = False

  if auto_send and email_address:
    send_email(email_address, notifyContextPath, email_subject, email_text)