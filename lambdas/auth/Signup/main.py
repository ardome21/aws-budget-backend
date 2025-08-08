import hashlib
import base64
import os
import json
import datetime
import boto3
from botocore.exceptions import ClientError
import jwt

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'http://localhost:4200',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Credentials': 'true'
}

dynamodb = boto3.resource('dynamodb')
userTable = dynamodb.Table('users-dev')


def check_password(password: str, stored_hash: str) -> bool:
    """Check if the provided password matches the stored hash"""
    try:
        decoded_hash_data = base64.b64decode(stored_hash.encode('utf-8'))
        salt = decoded_hash_data[:32]
        stored_pwdhash = decoded_hash_data[32:]
        computed_password_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 100000)
        return computed_password_hash == stored_pwdhash
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def verify_auth():
    """ Verify if user is logged in already and logs them in"""
    try:
        pass
    except Exception as e:
        print(f"Error verifying auth: {e}")
        return False


def login(event):
    """Login user"""
    try:
        if not event.get('body'):
            print("ERROR: No body in request")
            return {
                'statusCode': 400,
                'headers': {
                    **CORS_HEADERS,
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Request body is required'})
            }
        body = json.loads(event['body']) if isinstance(
            event.get('body'), str) else event.get('body', {})

        email = body.get('email')
        password = body.get('password')
        print(f"Email: {email}")

        if not email or not password:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Email and password are required'
                })
            }
        response = userTable.get_item(
            Key={'email': email}
        )
        stored_hash = None
        is_email_verified = False
        if 'Item' in response:
            user = response['Item']
            is_email_verified = user['email_verified']
            stored_hash = user['password_hash']
        else:
            # User does not exist
            print(f"User does not exist: {email}")
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'User does not exist'
                })
            }
        if not is_email_verified:
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Email not verified'
                })
            }
        if not stored_hash:
            # User exists but no password hash
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Invalid credentials'
                })
            }
        # Verify the password
        if check_password(password, stored_hash):
            print("Password verified")
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
            print(f"User profile: {userProfile}")
            is_development = True
            if is_development:
                cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=None; Max-Age=10; Path=/'
            else:
                cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'
            return {
                'statusCode': 200,
                'headers': {
                    **CORS_HEADERS,
                    'Content-Type': 'application/json',
                    'Set-Cookie': cookie_attributes
                },
                'body': json.dumps({
                    'message': 'Login successful',
                    'user': userProfile,
                        'expires_in': '86400 Second (24 hrs)'
                    })
                }
        else:
            print("Password verification failed")
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Invalid credentials'
                })
            }
    except Exception as e:
        print(f"Error logging in user: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
    
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

def verify_auth(event):
    token = get_auth_token(event)
    if not token:
        return not_authenticated_response()
    try:
        jwt_secret = boto3.client('ssm').get_parameter(Name='/budget/jwt-secret-key', WithDecryption=True)['Parameter']['Value']
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return not_authenticated_response('Token expired')
    except jwt.InvalidTokenError:
        return not_authenticated_response('Invalid token')
    response = userTable.get_item(Key={'email': payload.get("email")})

    if 'Item' not in response:
        return not_authenticated_response('User not found')

    user_data = {
        "email": response['Item'].get("email"),
        "first_name": response['Item'].get("first_name"),
        "last_name": response['Item'].get("last_name")
    }

    is_development = True
    if is_development:
        cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=None; Max-Age=10; Path=/'
    else:
        cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'


    return {
        'statusCode': 200,
        'headers': {
            **CORS_HEADERS,
            'Content-Type': 'application/json',
            'Set-Cookie': cookie_attributes
        },
        'body': json.dumps({
            'success': 'true',
            'userData': user_data,
            'message': 'Authenticated'
        })
    }


def lambda_handler(event, _context):
    """AWS Lambda handler for user login"""
    try:
        http_method = event.get('httpMethod') or event.get(
            'requestContext', {}).get('http', {}).get('method')
        if http_method == 'OPTIONS':
            print("Handling OPTIONS preflight request")
            return

        elif http_method == 'GET':
            print("Handling GET request")
            return verify_auth(event)
        elif http_method == 'POST':
            print("Handling POST request")
            return login(event)
        else:
            print(f"Unsupported HTTP method: {http_method}")
            return {
                'statusCode': 405,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Method not allowed'})
            }
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
