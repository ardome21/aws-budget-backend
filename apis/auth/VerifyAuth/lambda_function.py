import json
import os
import jwt
import boto3

def get_auth_token(event):
    cookies = event.get('cookies', [])
    for cookie in cookies:
        if cookie.startswith('authToken='):
            return cookie.split('=', 1)[1]
    return None

def not_authenticated_response(message='Not authenticated'):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Set-Cookie': 'authToken=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict'
        },
        'body': json.dumps({
            'success': 'false',
            'message': message
        }),
    }

def lambda_handler(event, context):
    token = get_auth_token(event)
    print(f"Received token: {token}")
    if not token:
        return not_authenticated_response()

    try:
        jwt_secret = boto3.client('ssm').get_parameter(Name='/budget/jwt-secret-key', WithDecryption=True)['Parameter']['Value']
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return not_authenticated_response('Token expired')
    except jwt.InvalidTokenError:
        return not_authenticated_response('Invalid token')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('budget-users')
    response = table.get_item(Key={'email': payload.get("email")})

    user_data = {
        "email": payload.get("email"),
        "first_name": response['Item'].get("first_name"),
        "last_name": response['Item'].get("last_name")
    }

    is_development = True
    if is_development:
        cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=None; Max-Age=172800; Path=/'
    else:
        cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'


    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'http://localhost:4200',
            'Access-Control-Allow-Credentials': 'true',
            'Set-Cookie': cookie_attributes
        },
        'body': json.dumps({
            'success': 'true',
            'userData': user_data,
            'message': 'Authenticated'
        }),
    }
