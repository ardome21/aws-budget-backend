import json
import os
import boto3
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
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
        # secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
        # secret_value = secrets_client.get_secret_value(SecretId="plaid")
        # secret = json.loads(secret_value["SecretString"])

        ssm_client = boto3.client('ssm')
        client_id = ssm_client.get_parameter(Name='/budget/plaid/client_id', WithDecryption=True)['Parameter']['Value']
        sandbox_secret = ssm_client.get_parameter(Name='/budget/plaid/sandbox_secret', WithDecryption=True)['Parameter']['Value']


        # Configure Plaid client
        configuration = Configuration(
            host=Environment.Sandbox,  # Use Environment.sandbox, Environment.development, or Environment.production
            api_key={
                'clientId': client_id,
                'secret': sandbox_secret # Make sure this key matches your secret
            }
        )
        
        api_client = ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        print(f'Event: {event}')  # Add logging for the event
        
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        access_token = body['access_token']
        print(f'Access_token: {access_token}')
        
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)        
        accounts = []
        for account in response.accounts:
            accounts.append({
                'account_id': account.account_id,
                'name': account.name,
                'type': str(account.type),
                'subtype': str(account.subtype) if account.subtype else None,
                'balance': {
                    'available': float(account.balances.available) if account.balances.available else None,
                    'current': float(account.balances.current) if account.balances.current else None
                }
            })
            
        print(f'Account: {accounts}')
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({'accounts': accounts})
        }
        
    except Exception as e:
        print(f'Error: {str(e)}')  # Add logging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }