from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
from lambdas.layers.open_meteo.open_meteo_api import OpenMeteoAPI
import json
import boto3
import os
import uuid
import decimal

_LOG = get_logger('Processor-handler')

def decimal_default(obj):
    if isinstance(obj, float):
        return decimal.Decimal(str(obj))
    raise TypeError

class Processor(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def lambda_handler(self, event, context):
        latitude = 52.52
        longitude = 13.41
        weather_api = OpenMeteoAPI(latitude, longitude)
        forecast = weather_api.get_latest_forecast()

        # Extract the necessary fields
        extracted_forecast = {
            "elevation": decimal.Decimal(str(forecast.get("elevation", 0))),
            "generationtime_ms": decimal.Decimal(str(forecast.get("generationtime_ms", 0))),
            "hourly": {
                "temperature_2m": [decimal.Decimal(str(temp)) for temp in
                                   forecast.get("hourly", {}).get("temperature_2m", [])],
                "time": forecast.get("hourly", {}).get("time", [])
            },
            "hourly_units": {
                "temperature_2m": forecast.get("hourly_units", {}).get("temperature_2m"),
                "time": forecast.get("hourly_units", {}).get("time")
            },
            "latitude": decimal.Decimal(str(forecast.get("latitude", 0))),
            "longitude": decimal.Decimal(str(forecast.get("longitude", 0))),
            "timezone": forecast.get("timezone"),
            "timezone_abbreviation": forecast.get("timezone_abbreviation"),
            "utc_offset_seconds": forecast.get("utc_offset_seconds", 0)
        }

        print(f'Extracted Format::'+str(extracted_forecast))

        # Generate a unique ID
        record_id = str(uuid.uuid4())

        # Create the record to be inserted into DynamoDB
        record = {
            'id': record_id,
            'forecast': extracted_forecast
        }

        # Dynamo DB
        region = os.environ.get('region', 'eu-central-1')
        table_name = os.environ.get('target_table', 'Weather')

        dynamodb = boto3.resource('dynamodb', region_name=region)
        table = dynamodb.Table(table_name)

        # Insert the record into DynamoDB
        table.put_item(Item=record)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Record inserted', 'record_id': record_id})
        }

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = Processor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
