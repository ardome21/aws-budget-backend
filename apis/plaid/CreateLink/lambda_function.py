import json
import boto3
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment

def lambda_handler(event, context):
    try:
        # Get secrets from AWS Secrets Manager
        secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
        secret_value = secrets_client.get_secret_value(SecretId="plaid")
        secret = json.loads(secret_value["SecretString"])
        
        # Configure Plaid client
        configuration = Configuration(
            host=Environment.Sandbox,  # Use Environment.sandbox, Environment.development, or Environment.production
            api_key={
                'clientId': secret['client_id'],
                'secret': secret['sandbox_secret']  # Make sure this key matches your secret
            }
        )
        api_client = ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        
        # Parse the request if needed (for POST requests with user data)
        if event.get('body'):
            body = json.loads(event['body'])
            user_id = body.get('user_id', 'unique_user_id_123')
        else:
            user_id = 'unique_user_id_123'
        
        # Create link token request
        request = LinkTokenCreateRequest(
            products=[Products('transactions')],
            client_name="Your App Name",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            )
        )
        
        # Create the link token
        response = client.link_token_create(request)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'link_token': response['link_token']
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to create link token'
            })
        }