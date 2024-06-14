from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json
import logging

_LOG = get_logger('SqsHandler-handler')
# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SqsHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def lambda_handler(self, event, context):
        # Log the entire event for debugging purposes
        logger.info('Received event: %s', json.dumps(event))

        # Loop through the SQS records
        for record in event['Records']:
            sqs_message = record['body']

            # Log the SQS message
            logger.info('SNS Message: %s', sqs_message)

        return {
            'statusCode': 200,
            'body': json.dumps('Message logged successfully')
        }

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = SqsHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
