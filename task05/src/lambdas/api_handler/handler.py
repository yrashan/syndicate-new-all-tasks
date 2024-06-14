from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json
import uuid
from datetime import datetime
import boto3
import os

_LOG = get_logger('ApiHandler-handler')


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def lambda_handler(self, event, context):
        # Parse the body of the request
        body = json.loads(event['body'])

        # Extract the principalId and content from the request
        principal_id = body['principalId']
        content = body['content']

        # Generate UUID v4
        generated_id = str(uuid.uuid4())

        # Get the current timestamp in ISO format
        created_at = datetime.utcnow().isoformat()

        # Create the response
        response_event = {
            "id": generated_id,
            "principalId": principal_id,
            "createdAt": created_at,
            "body": content
        }

        # Dynamo DB
        region = os.environ.get('region','eu-central-1')
        table_name = os.environ.get('target_table', 'Events')

        print("region:::::"+region)
        print("table_name:::::" + table_name)

        dynamodb = boto3.resource('dynamodb', region_name=region)
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=response_event)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'statusCode': 201,
                'event': response_event
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
