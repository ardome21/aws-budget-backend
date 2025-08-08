import json
import boto3
from plaid.api import plaid_api
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment
 
CORS_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, DELETE',
        'Access-Control-Max-Age': '86400'
    }

def exchange_public_token(client, public_token):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    
    access_token = response['access_token']
    item_id = response['item_id']
    return {
        'access_token': access_token,
        'item_id': item_id
    }

def lambda_handler(event, context):
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    print(f"HTTP Method detected: {http_method}")
    
    if http_method == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': ''
        }
    
    try:
        http_method = event.get('httpMethod') or event.get(
            'requestContext', {}).get('http', {}).get('method')
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
        api_client = ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        if not client:
            raise Exception("Plaid client not initialized")
        print(f"Plaid client initialized")
        
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        public_token = body['public_token']
        if  not public_token:
            raise Exception("No public token provided")
        print(f"Public token received: {public_token}")
        
        tokens = exchange_public_token(client, public_token) 
        if not (tokens and tokens['access_token'] and tokens['item_id']):
            raise Exception("No tokens received")
        print(f"Tokens received: {tokens}")       
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(tokens)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }