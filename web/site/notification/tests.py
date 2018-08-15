# (c) 2018 Tim Sawyer, All Rights Reserved

from django.test import TestCase
from notification.notify import MessageWrapper

class MockClient:
    messages = None

    def __init__(self):
        self.messages = []

    def publish(self, TopicArn, Message):
        self.messages.append(Message)


class MessageWrapperTestCase(TestCase):
    def testSendAllNone(self):

        lExpectedMessage = """{"notification": {
  "module" : "None",
  "type" : "None",
  "change" : "None",
  "user" : "None",
  "ip" : "",
  "browser" : "",
  "destination" : "None",
  "cc" : "None",
  "bcc" : "None",
  "fromName" : "None",
  "fromEmail" : "None",
  "thingOld" : null,
  "thingNew" : null
}"""


        lTestMessage = MessageWrapper(
            pThingOld = None, 
            pThingNew = None, 
            pModule = None, 
            pObjectType = None, 
            pChangeType = None, 
            pUser = None, 
            pBrowserDetails = None, 
            pDestination = None, 
            pAdditionalContext = None, 
            pCc = None, 
            pBcc = None, 
            pFromName = None, 
            pFromEmail = None,
            )
        lMockClient = MockClient()
        lTestMessage.send(lMockClient)
        self.assertEqual(len(lMockClient.messages), 1)
        self.assertEqual(lExpectedMessage, lMockClient.messages[0])