import boto3
import json
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment


def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        print(f"HTTP Method detected: {http_method}")
        
        if http_method == 'OPTIONS':
            print("Handling OPTIONS preflight request")
            return

        ssm_client = boto3.client('ssm')
        client_id = ssm_client.get_parameter(Name='/budget/plaid/client_id', WithDecryption=True)['Parameter']['Value']
        sandbox_secret = ssm_client.get_parameter(Name='/budget/plaid/sandbox_secret', WithDecryption=True)['Parameter']['Value']

        configuration = Configuration(
            host=Environment.Sandbox,
            api_key={
                'clientId': client_id,
                'secret': sandbox_secret
            }
        )
        
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        user_id = body['user_id']
        print(f'User ID: {user_id}')

        api_client = ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        request = LinkTokenCreateRequest(
            products=[Products("auth"), Products("transactions")],
            client_name="My App",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=user_id)
        )

        response = client.link_token_create(request)
        return {
            'statusCode': 200,
            'body': json.dumps(response.to_dict())
        }
        
    except Exception as e:
        print(f'Error: {str(e)}')  # Add logging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }