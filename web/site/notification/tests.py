# (c) 2018 Tim Sawyer, All Rights Reserved

from django.test import TestCase
from notification.notify import MessageWrapper

class MockClient:
    """
    Mock boto3 style client mirroring SNS interface
    """
    messages = None

    def __init__(self):
        self.messages = []

    def publish(self, TopicArn, Message):
        self.messages.append(Message)


class MessageWrapperTestCase(TestCase):

    def testSendAllNone(self):
        """
        Send with all values passed in as None
        """
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
        self.assertEqual(len(lMockClient.messages), 0)
        lTestMessage.send(lMockClient)
        self.assertEqual(len(lMockClient.messages), 1)
        self.assertEqual(lExpectedMessage, lMockClient.messages[0])


    def testSendNoThings(self):
        """
        Test send with all values filled in except things
        """
        lExpectedMessage = """{"notification": {
  "module" : "contests",
  "type" : "contest",
  "change" : "edit",
  "user" : "test",
  "ip" : "127.0.0.1",
  "browser" : "Netscape Navigator",
  "destination" : "destination@brassbandresults.co.uk",
  "cc" : "cc@brassbandresults.co.uk",
  "bcc" : "bcc@brassbandresults.co.uk",
  "fromName" : "Tim Sawyer",
  "fromEmail" : "source@brassbandresults.co.uk",
  "thingOld" : null,
  "thingNew" : null
}"""

        lTestMessage = MessageWrapper(
            pThingOld = None, 
            pThingNew = None, 
            pModule = "contests", 
            pObjectType = "contest", 
            pChangeType = "edit", 
            pUser = "test", 
            pBrowserDetails = ("127.0.0.1", "Netscape Navigator"), 
            pDestination = "destination@brassbandresults.co.uk", 
            pAdditionalContext = None, 
            pCc = "cc@brassbandresults.co.uk", 
            pBcc = "bcc@brassbandresults.co.uk", 
            pFromName = "Tim Sawyer", 
            pFromEmail = "source@brassbandresults.co.uk",
            )
        lMockClient = MockClient()
        self.assertEqual(len(lMockClient.messages), 0)
        lTestMessage.send(lMockClient)
        self.assertEqual(len(lMockClient.messages), 1)
        self.assertEqual(lExpectedMessage, lMockClient.messages[0])