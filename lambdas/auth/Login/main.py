import hashlib
import base64
import json
from datetime import datetime, timedelta, timezone
import boto3
from boto3.dynamodb.conditions import Key
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

def login(event):
    """Login user"""
    try:
        if not event.get('body'):
            print("ERROR: No body in request")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
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
        response = userTable.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email)
            )
        if 'Items' not in response['Items']:
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'User does not exist'
                })
            }
        if len(response['Items']) > 1:
            return {
                'statusCode': 500,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': 'Multiple users found'
                })
            }
        user = response['Items'][0]
        is_email_verified = user['email_verified']
        stored_hash = user['password_hash']
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
                'exp': datetime.now(timezone.utc) + timedelta(hours=48)
            }

            jwt_secret = boto3.client('ssm').get_parameter(Name='/budget/jwt-secret-key', WithDecryption=True)['Parameter']['Value']
            token = jwt.encode(payload, jwt_secret, algorithm='HS256')

            userProfile = {
                    'email': email,
                    'user_id': user['user_id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name']
                }
            print(f"User profile: {userProfile}")
            is_development = True
            if is_development:
                cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=None; Max-Age=172800; Path=/'
            else:
                cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'
            return {
                'statusCode': 200,
                'headers': {
                    **CORS_HEADERS,
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
    is_development = True
    if is_development:
        cookie_attributes = 'authToken=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=None'
    else:
        cookie_attributes = 'authToken=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict'
    return {
        'statusCode': 200,
        'headers': {
            **CORS_HEADERS,
            'Set-Cookie': cookie_attributes
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
    response = userTable.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(payload.get("email"))
    )

    if 'Items' not in response['Items']:
        return not_authenticated_response('User not found')

    if len(response['Items']) > 1:
        return not_authenticated_response('Multiple users found')
    user = response['Items'][0]

    user_data = {
        "email": user.get("email"),
        "user_id": user.get("user_id"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name")
    }

    is_development = True
    if is_development:
        cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=None; Max-Age=172800; Path=/'
    else:
        cookie_attributes = f'authToken={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'


    return {
        'statusCode': 200,
        'headers': {
            **CORS_HEADERS,
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
            print("Handling GET request: Verify Auth Status")
            return verify_auth(event)
        elif http_method == 'POST':
            print("Handling POST request: User Login")
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
