from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json
import uuid
import boto3
import os
from datetime import datetime

_LOG = get_logger('UuidGenerator-handler')


class UuidGenerator(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def lambda_handler(self, event, context):
        # Generate 10 random UUIDs
        ids = [str(uuid.uuid4()) for _ in range(10)]

        # Get the current time in ISO format and truncate milliseconds
        now = datetime.utcnow()
        execution_start_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        # Create the content for the file
        content = {
            "ids": ids
        }

        # Convert content to JSON string
        json_content = json.dumps(content)

        # Define the S3 bucket and file name
        bucket_name = os.environ.get('target_bucket', 'uuid-storage')
        file_name = f"{execution_start_time}"

        # Initialize boto3 S3 client
        s3_client = boto3.client('s3')

        # Upload the JSON file to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json_content,
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps('File created successfully!')
        }

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = UuidGenerator()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
