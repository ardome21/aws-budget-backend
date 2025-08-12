import json

def lambda_handler(event, _context):

    try:
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        if http_method == 'OPTIONS':
            print("Handling OPTIONS preflight request")
            return
        
        cookie_attributes = f'authToken=; HttpOnly; Secure; SameSite=None; Max-Age=172800; Path=/'
        if http_method == 'POST':
            print("Handling logout request")
            return {
                'statusCode': 200,
                'headers': {
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
            'body': json.dumps({
                'error': f'Internal server error {e}'
            })
        }