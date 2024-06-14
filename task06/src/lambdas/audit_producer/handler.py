from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json
import boto3
import uuid
import os
from datetime import datetime

_LOG = get_logger('AuditProducer-handler')

table_name = os.environ.get('target_table', 'Audit')
dynamodb = boto3.resource('dynamodb')
audit_table = dynamodb.Table(table_name)


def process_insert(new_image):
    item_key = new_image['key']['S']
    new_value = {k: v['S'] if 'S' in v else int(v['N']) for k, v in new_image.items()}
    audit_item = {
        'id': str(uuid.uuid4()),
        'itemKey': item_key,
        'modificationTime': datetime.utcnow().isoformat(),
        'newValue': new_value
    }
    audit_table.put_item(Item=audit_item)


def process_modify(old_image, new_image):
    item_key = new_image['key']['S']
    for attribute in old_image:
        old_value = old_image[attribute]['S'] if 'S' in old_image[attribute] else old_image[attribute]['N']
        new_value = new_image[attribute]['S'] if 'S' in new_image[attribute] else new_image[attribute]['N']
        if old_value != new_value:
            audit_item = {
                'id': str(uuid.uuid4()),
                'itemKey': item_key,
                'modificationTime': datetime.utcnow().isoformat(),
                'updatedAttribute': attribute,
                'oldValue': old_value,
                'newValue': new_value
            }
            audit_table.put_item(Item=audit_item)

class AuditProducer(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def lambda_handler(self, event, context):
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                new_image = record['dynamodb']['NewImage']
                process_insert(new_image)
            elif record['eventName'] == 'MODIFY':
                old_image = record['dynamodb']['OldImage']
                new_image = record['dynamodb']['NewImage']
                process_modify(old_image, new_image)

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = AuditProducer()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
