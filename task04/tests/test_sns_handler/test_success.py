from tests.test_sns_handler import SnsHandlerLambdaTestCase


class TestSuccess(SnsHandlerLambdaTestCase):

    def test_success(self):
        event = {
          "Records": [
            {
              "EventSource": "aws:sns",
              "EventVersion": "1.0",
              "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55",
              "Sns": {
                "Type": "Notification",
                "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                "TopicArn": "arn:aws:sns:us-east-1:123456789012:MyTopic",
                "Subject": "Test Subject",
                "Message": "{\"key1\": \"value1\", \"key2\": \"value2\"}",
                "Timestamp": "2024-06-14T00:00:00.000Z",
                "SignatureVersion": "1",
                "Signature": "EXAMPLEpH+..",
                "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-0123456789abcdef.pem",
                "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:123456789012:MyTopic:2bcfbf39-05c3-41de-beaa-fcfcc21c8f55",
                "MessageAttributes": {
                  "attribute1": {
                    "Type": "String",
                    "Value": "value1"
                  },
                  "attribute2": {
                    "Type": "Binary",
                    "Value": "value2"
                  }
                }
              }
            }
          ]
        }
        self.assertEqual(self.HANDLER.handle_request(event, dict()), 200)

