# (c) 2018 Tim Sawyer, All Rights Reserved

import os
import json
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

  if notifyContextPath == "feedback.feedback.new":
    email_subject = "Feedback" 
    email_text = parsedMessage["notification"]["message"]
    email_text = email_text.replace("!NEW_LINE!", "\n")
    email_text = email_text.replace("&#39;", "'")
    email_address = parsedMessage["notification"]["destination"]
    if email_address == "None":
      email_address = None

    if email_address == None:
      email_address = "feedback@brassbandresults.co.uk"

    print ("Sending email to %s for notification %s" % (email_address, notifyContextPath))

    ses_client = boto3.client('ses',region_name='eu-west-1')
    response = ses_client.send_email(
      Source='BrassBandResults <contact@brassbandresults.co.uk>',
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
