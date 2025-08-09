import json
import hashlib
import os
import base64
import re
import boto3
from datetime import datetime
import uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('users-dev')

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA256"""
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    combined = salt + pwdhash
    return base64.b64encode(combined).decode('utf-8')

def create_user_record(email: str, firstName: str, lastName: str, hashed_password: str, verification_token: str):
    """Create user record in database"""
    timestamp = datetime.utcnow().isoformat()
    
    user_item = {
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'password_hash': hashed_password,
        'created_at': timestamp,
        'updated_at': timestamp,
        'is_active': True,
        'email_verified': False,
        'verification_token': verification_token
    }
    
    try:
        users_table.put_item(Item=user_item)
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        raise

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def check_user_exists(email: str) -> bool:
    """Check if user already exists"""
    try:
        response = users_table.get_item(Key={'email': email})
        return 'Item' in response
    except Exception as e:
        print(f"Error checking user existence: {str(e)}")
        return False

def send_email(user_email: str, user_first_name: str, user_last_name: str, verification_token: str):
    """Send end email using SES"""
    ses = boto3.client('ses', region_name='us-east-1')
    sender_email = 'ardome21+aws@gmail.com'
    subject = 'Confirm Email for Budget App'
    confirmation_link = f"https://kdg0ldohqb.execute-api.us-east-1.amazonaws.com/default/budget-verify-account?email={user_email}&token={verification_token}"

    body = f"""
    <html>
    <body>
        <h1>Welcome to Budget App, {user_first_name} {user_last_name}!</h1>
        <p>Thank you for joining Budget App. We're excited to have you on board.</p>
        <p>Please click the link to confirm this email and user</p>
        <a href="{confirmation_link}">
        <p>Best regards,<br>Budget App Team</p>
    </body>
    </html>
    """

    try:
        ses.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body}}
            }
        )
        print(f"End email sent to {user_email}")
    except Exception as e:
        print(f"Error sending end email: {str(e)}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler for creating users"""
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
    
    try:
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        print(f"HTTP Method detected: {http_method}")
        
        if http_method == 'OPTIONS':
            print("Handling OPTIONS preflight request")
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        print("Handling POST request")
        # Parse request body
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if field not in body or not body[field]]
        
        if missing_fields:
            print(f"Missing required fields: {', '.join(missing_fields)}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'success': False
                })
            }
        
        email = body['email'].lower().strip()
        password = body['password']
        firstName = body['first_name'].strip()
        lastName = body['last_name'].strip()
        
        print(f"Email: {email}, First Name: {firstName}, Last Name: {lastName}")
        
        # # Validate email format
        # if not validate_email(email):
        #     print(f"Invalid email format: {email}")
        #     return {
        #         'statusCode': 400,
        #         'headers': headers,
        #         'body': json.dumps({
        #             'error': 'Invalid email format',
        #             'success': False
        #         })
        #     }
        
        # # Check password strength (minimum 8 characters)
        # if len(password) < 6:
        #     print(f"Password too short: {password}")
        #     return {
        #         'statusCode': 400,
        #         'headers': headers,
        #         'body': json.dumps({
        #             'error': 'Password must be at least 8 characters long',
        #             'success': False
        #         })
        #     }
        
        # # Check if user already exists
        # if check_user_exists(email):
        #     print(f"User already exists: {email}")
        #     return {
        #         'statusCode': 409,
        #         'headers': headers,
        #         'body': json.dumps({
        #             'error': 'User with this email already exists',
        #             'success': False
        #         })
        #     }
        
        # Hash password and create user
        hashed_password = hash_password(password)
        verification_token = str(uuid.uuid4())
        
        create_user_record(
            email=email,
            firstName=firstName,
            lastName=lastName,
            hashed_password=hashed_password,
            verification_token=verification_token
        )
        print(f"User created successfully: {email}")
        send_email(email, firstName, lastName, verification_token)
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'message': 'User created successfully',
                'user': {
                    'email': email,
                    'firstName': firstName,
                    'lastName': lastName
                },
                'success': True
            })
        }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Invalid JSON format',
                'success': False
            })
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'success': False
            })
        }