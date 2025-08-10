import json
import boto3
from datetime import datetime
from plaid.api import plaid_api
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
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

def get_institution_name(client, access_token):
    """Get institution name for"""
    try:
        from plaid.model.item_get_request import ItemGetRequest
        request = ItemGetRequest(access_token=access_token)
        response = client.item_get(request)
        institution_id = response['item']['institution_id']
        
        # Get institution details
        inst_request = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        inst_response = client.institutions_get_by_id(inst_request)
        return inst_response['institution']['name']
    except Exception as e:
        print(f"Could not fetch institution name: {e}")
        return None
    
def store_plaid_connection(user_id, access_token, item_id, institution_name=None):
    """Store the Plaid connection details in DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('plaid_connections')
    
    item = {
        'user_id': user_id,
        'access_token': access_token,
        'item_id': item_id,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'active'
    }
    
    if institution_name:
        item['institution_name'] = institution_name
    
    table.put_item(Item=item)
    return item

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
        user_id = body['user_id']
        if not user_id:
            raise Exception("No user id provided ")
        public_token = body['public_token']
        if not public_token:
            raise Exception("No public token provided")
        print(f"Public token received for {user_id}")
        
        tokens = exchange_public_token(client, public_token) 
        if not (tokens and tokens['access_token'] and tokens['item_id']):
            raise Exception("No tokens received")
        institution_name = get_institution_name(client, tokens['access_token'])

        stored_connection = store_plaid_connection(
            user_id=user_id,
            access_token=tokens['access_token'],
            item_id=tokens['item_id'],
            institution_name=institution_name
        )
        
        print(f"Stored Plaid connection for user {user_id}")
        
        # Return success (don't send access_token back to frontend for security)
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'success': True,
                'item_id': tokens['item_id'],
                'institution_name': institution_name,
                'message': 'Bank account connected successfully'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }