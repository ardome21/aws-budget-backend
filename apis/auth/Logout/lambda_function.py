import json

def lambda_handler(event, context):
    origin = 'http://localhost:4200'
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    print(f"HTTP Method detected: {http_method}")
    
    if http_method == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    is_development = True
    if is_development:
        cookie_attributes = f'authToken=; HttpOnly; Secure; SameSite=None; Max-Age=172800; Path=/'
    else:
        cookie_attributes = f'authToken=; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'

    
    if http_method == 'POST':
        print("Handling logout request")
        logout_headers = {
            **headers,
            'Set-Cookie':  cookie_attributes
        }
        
        return {
            'statusCode': 200,
            'headers': logout_headers,
            'body': json.dumps({
                'success': True,
                'message': 'Successfully logged out'
            })
        }
    
    return {
        'statusCode': 405,
        'headers': {**headers, 'Allow': 'POST, OPTIONS'},
        'body': json.dumps({'success': False, 'error': 'Method not allowed'})
    }