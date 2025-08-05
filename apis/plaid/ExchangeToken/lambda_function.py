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
    
    print("Event:", json.dumps(event, indent=2))
    
    # Handle preflight OPTIONS request (works for both API Gateway v1.0 and v2.0)
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
        print("Event:", json.dumps(event, indent=2))
        secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
        secret_value = secrets_client.get_secret_value(SecretId="plaid")
        secret = json.loads(secret_value["SecretString"])
        
        configuration = Configuration(
            host=Environment.Sandbox,
            api_key={
                'clientId': secret['client_id'],
                'secret': secret['sandbox_secret']
            }
        )
        api_client = ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        public_token = body['public_token']
        
        tokens = exchange_public_token(client, public_token)
        print(f"Tokens: {tokens}")
        
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