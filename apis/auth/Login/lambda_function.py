import hashlib
import base64
import os
import json
import datetime
import boto3
from botocore.exceptions import ClientError
import jwt

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA256"""
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    combined = salt + pwdhash
    return base64.b64encode(combined).decode('utf-8')

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash"""
    try:
        combined = base64.b64decode(stored_hash.encode('utf-8'))
        salt = combined[:32]
        stored_pwdhash = combined[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwdhash == stored_pwdhash
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def lambda_handler(event, context):
    """AWS Lambda handler for user login"""
    try:
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        print(f"HTTP Method detected: {http_method}")
        
        # CORS headers for all responses
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true'
        }
        
        if http_method == 'OPTIONS':
            print("Handling OPTIONS preflight request")
            return {
                'statusCode': 200,
                'headers': {
                    **cors_headers,
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        
        if http_method == 'POST':
            print("Handling POST request")
            
            # Parse request body
            if not event.get('body'):
                print("ERROR: No body in request")
                return {
                    'statusCode': 400,
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'Request body is required'})
                }
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Email and password are required'
                })
            }
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('budget-users')
        
        response = table.get_item(
            Key={'email': email}
        )
        stored_hash = None
        is_email_verified = False
        if 'Item' in response:
            user = response['Item']
            is_email_verified = user['email_verified']
            stored_hash = user['password_hash']
        else:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'User does not exist'
                })
            }
        
        if not is_email_verified:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Email not verified'
                })
            }
        
        if not stored_hash:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid credentials'
                })
            }
        
        # Verify the password
        if verify_password(password, stored_hash):
            payload = {
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=48)
            }
            
            jwt_secret = boto3.client('ssm').get_parameter(Name='/budget/jwt-secret-key', WithDecryption=True)['Parameter']['Value']
            token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            userProfile = {
                'email': email,
                'first_name': user['first_name'],
                'last_name': user['last_name']
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
                    'message': 'Login successful',
                    'user': userProfile,
                    'expires_in': '86400 Second (24 hrs)'
                })
            }
        else:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid credentials'
                })
            }
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }