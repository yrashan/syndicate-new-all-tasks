from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import json
import boto3
import uuid
import os
import decimal
import typing as t
#import datetime
from datetime import datetime
from boto3.dynamodb.conditions import Key

_LOG = get_logger('ApiHandler-handler')

region = os.environ.get('region', 'eu-central-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
cognito_client = boto3.client('cognito-idp')

USER_POOL_NAME = os.environ.get('booking_userpool', 'simple-booking-userpool')
USER_POOL_CLIENT_NAME = "cmtr-7e0ff3c4-client-app"

# Dynamo DB
tables_table_db = os.environ.get('tables_table', 'Tables')
reservations_table_db = os.environ.get('reservations_table', 'Reservations')

tables_table = dynamodb.Table(tables_table_db)
reservations_table = dynamodb.Table(reservations_table_db)

class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def lambda_handler(self, event, context):
        try:
            # Logging the event
            print(f"Received event: {json.dumps(event)}")
            _LOG.info(f"Received event:: {json.dumps(event)}")

            # Extract path and method from the proxy event structure
            path = event.get('resource', '')
            method = event.get('httpMethod', '')

            if path == '/signup' and method == 'POST':
                return self.signup(event)
            elif path == '/signin' and method == 'POST':
                return self.signin(event)
            elif path == '/tables' and method == 'POST':
                return self.create_table(event)
            elif path == '/tables' and method == 'GET':
                return self.list_tables(event)
            elif path.startswith('/tables/') and method == 'GET':
                return self.get_table(event)
            elif path == '/reservations' and method == 'POST':
                return self.create_reservation(event)
            elif path == '/reservations' and method == 'GET':
                return self.list_reservations(event)
            else:
                return {'statusCode': 400, 'body': json.dumps('Bad Request')}
        except Exception as e:
            _LOG.error(f"Failed to handle request: {e}")
            return {"statusCode": 400}


    def get_user_pool_id(self, user_pool_name):

        user_pool_id = None
        response = cognito_client.list_user_pools(MaxResults=50)
        _LOG.info(f"User pools: {response}")

        for user_pool in response["UserPools"]:
            if user_pool["Name"] == user_pool_name:
                user_pool_id = user_pool["Id"]
                break

        if user_pool_id is None:
            raise ValueError(f"User pool {USER_POOL_NAME} not found")

        return user_pool_id

    def get_user_pool_client_id(self, user_pool_id):

        client_id = None
        response = cognito_client.list_user_pool_clients(
            UserPoolId=user_pool_id,
            MaxResults=50
        )
        _LOG.info(f"User pool clients: {response}")

        for client in response["UserPoolClients"]:
            if client["ClientName"] == USER_POOL_CLIENT_NAME:
                client_id = client["ClientId"]
                break

        if client_id is None:
            raise ValueError(f"User pool client not found")

        return client_id

    def serialize(self, data: t.Any) -> t.Any:

        if isinstance(data, list):
            return [self.serialize(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.serialize(value) for key, value in data.items()}
        elif isinstance(data, decimal.Decimal):
            return int(data)

        return data

    def is_overlapping(
            self,
            start1: str,
            end1: str,
            start2: str,
            end2: str,
    ) -> bool:

        start1 = datetime.strptime(start1, "%H:%M").time()
        end1 = datetime.strptime(end1, "%H:%M").time()
        start2 = datetime.strptime(start2, "%H:%M").time()
        end2 = datetime.strptime(end2, "%H:%M").time()

        if start1 <= start2 <= end1 or start1 <= end2 <= end1:
            return True

        return False

    def signup(self, event):
        # Logging the event body
        body = json.loads(event.get('body'))
        first_name = body['firstName']
        last_name = body['lastName']
        email = body['email']
        password = body['password']

        user_pool_id = self.get_user_pool_id(USER_POOL_NAME)

        try:
            response = cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'given_name', 'Value': first_name},
                    {'Name': 'family_name', 'Value': last_name},
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                MessageAction='SUPPRESS',
                TemporaryPassword=password
            )
            _LOG.info(f"create user response: {response}")

            response = cognito_client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=email,
                Password=password,
                Permanent=True,
            )
            _LOG.info(f"set user password response: {response}")

            return {'statusCode': 200, 'body': json.dumps('Sign-up process is successful')}
        except cognito_client.exceptions.UserLambdaValidationException as e:
            return {'statusCode': 400, 'body': json.dumps(f'Error: {str(e)}')}

    def signin(self, event):
        body = json.loads(event.get('body'))
        _LOG.info(f"Signin body type: {type(body)}")
        _LOG.info(f"Signin body: {body}")
        email = body['email']
        password = body['password']

        _LOG.info(f"email: {email}")

        user_pool_id = self.get_user_pool_id(USER_POOL_NAME)
        client_id = self.get_user_pool_client_id(user_pool_id)

        try:
            response = cognito_client.initiate_auth(
                ClientId=client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'accessToken': response['AuthenticationResult']['IdToken']})
            }
        except cognito_client.exceptions.NotAuthorizedException as e:
            return {'statusCode': 400, 'body': json.dumps(f'Error: {str(e)}')}

    def create_table(self, event):
        body = json.loads(event.get('body'))
        table_id = int(body["id"])
        item = {
            'id': table_id,
            'number': int(body['number']),
            'places': int(body['places']),
            'isVip': bool(body['isVip']),
            'minOrder': body.get('minOrder', None)
        }
        tables_table.put_item(Item=item)
        return {'statusCode': 200, 'body': json.dumps({'id': table_id})}

    # def get_next_table_id(self):
    #     response = tables_table.scan()
    #     items = response['Items']
    #     if not items:
    #         return 1
    #     max_id = max(item['id'] for item in items)
    #     return max_id + 1

    def list_tables(self, event):
        _LOG.info("Getting tables")
        response = tables_table.scan()
        tables = response["Items"]
        tables = self.serialize(tables)
        tables = sorted(tables, key=lambda table: table["id"])
        _LOG.info(f"Getting tables:: {tables}")
        return {
            "statusCode": 200,
            "body": json.dumps({'tables': tables})
        }
        return {'statusCode': 200, 'body': json.dumps({'tables': response['Items']})}

    def get_table(self, event):
        table_id = int(event['pathParameters']['tableId'])
        _LOG.info(f"Getting table: {table_id}")
        response = tables_table.get_item(Key={"id": table_id})
        table = response["Item"]
        table = self.serialize(table)
        if 'Item' in response:
            return {'statusCode': 200, 'body': json.dumps(table)}
        else:
            return {'statusCode': 400, 'body': json.dumps('Table not found')}

    def create_reservation(self, event):
        body = json.loads(event.get('body'))
        table_number = int(body['tableNumber'])
        slot_date = body['date']
        slot_time_start = body['slotTimeStart']
        slot_time_end = body['slotTimeEnd']

        # Check if the table number exists
        response = tables_table.scan()
        tables = response["Items"]
        for table in tables:
            if table["number"] == table_number:
                break
        else:
            raise ValueError(f"Table {table_number} not found")

        # Check if there is any overlap
        response = reservations_table.scan()
        reservations = response["Items"]
        reservations = self.serialize(reservations)
        for reservation in reservations:
            if reservation["tableNumber"] == table_number and reservation["date"] == slot_date:
                reservation_start = reservation["slotTimeStart"]
                reservation_end = reservation["slotTimeEnd"]
                if self.is_overlapping(reservation_start, reservation_end, slot_time_start, slot_time_end):
                    raise ValueError("Reservation time is overlapping with another reservation")

        reservation_id = str(uuid.uuid4())
        item = {
            'id': reservation_id,
            'tableNumber': table_number,
            'clientName': body['clientName'],
            'phoneNumber': body['phoneNumber'],
            'date': slot_date,
            'slotTimeStart': slot_time_start,
            'slotTimeEnd': slot_time_end
        }
        reservations_table.put_item(Item=item)
        return {'statusCode': 200, 'body': json.dumps({'reservationId': reservation_id})}

    def list_reservations(self, event):
        response = reservations_table.scan()
        reservations = response["Items"]
        reservations = self.serialize(reservations)
        return {'statusCode': 200, 'body': json.dumps({'reservations': reservations})}

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
