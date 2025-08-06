import json

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'http://localhost:4200',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Credentials': 'true'
}

def lambda_handler(event, _context):

    try:
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        if http_method == 'OPTIONS':
            print("Handling OPTIONS preflight request")
            return

        is_development = True
        if is_development:
            cookie_attributes = f'authToken=; HttpOnly; Secure; SameSite=None; Max-Age=172800; Path=/'
        else:
            cookie_attributes = f'authToken=; HttpOnly; Secure; SameSite=Strict; Max-Age=172800; Path=/'

        if http_method == 'POST':
            print("Handling logout request")
            return {
                'statusCode': 200,
                'headers': {
                    **CORS_HEADERS,
                    'Set-Cookie': cookie_attributes
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Successfully logged out'
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': f'Internal server error {e}'
            })
        }