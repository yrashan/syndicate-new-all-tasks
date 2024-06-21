from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
from lambdas.layers.open_meteo.open_meteo_api import OpenMeteoAPI
import json

_LOG = get_logger('ApiHandler-handler')


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def lambda_handler(self, event, context):
        path = event.get('rawPath', '/')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')

        if path == '/weather' and method == 'GET':
            latitude = 52.52
            longitude = 13.41
            weather_api = OpenMeteoAPI(latitude, longitude)
            forecast = weather_api.get_latest_forecast()
            return {
                'statusCode': 200,
                'body': json.dumps(forecast)
            }
        else:
            return {
                "statusCode": 400,
                "body": f'{{"statusCode": 400, "message": "Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}"}}'
            }

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
