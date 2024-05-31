from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger('HelloWorld-handler')


class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def lambda_handler(self, event, context):
        path = event.get('rawPath', '/')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')

        if path == '/hello' and method == 'GET':
            return {
                "statusCode": 200,
                "body": '{"message": "Hello from Lambda"}'
            }
        else:
            return {
                "statusCode": 400,
                "body": f'{{"message": "Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}"}}'
            }

    def handle_request(self, event, context):
        response = self.lambda_handler(event, context)
        return response["statusCode"]
    

HANDLER = HelloWorld()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
