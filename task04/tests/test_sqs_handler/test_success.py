from tests.test_sqs_handler import SqsHandlerLambdaTestCase


class TestSuccess(SqsHandlerLambdaTestCase):

    def test_success(self):
        event = {
            "Records": [
                {
                    "messageId": "1c6e9a1d-0ff6-4f37-bf4d-7d1b6238e3b3",
                    "receiptHandle": "AQEBB8f6...2X1JQ==",
                    "body": "{\"key1\": \"value1\", \"key2\": \"value2\"}",
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1523232000000",
                        "SenderId": "AIDAI8M2...4H3P",
                        "ApproximateFirstReceiveTimestamp": "1523232000001"
                    },
                    "messageAttributes": {},
                    "md5OfBody": "b1946ac92492d2347c6235b4d2611184",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                    "awsRegion": "us-east-1"
                }
            ]
        }
        self.assertEqual(self.HANDLER.handle_request(event, dict()), 200)

