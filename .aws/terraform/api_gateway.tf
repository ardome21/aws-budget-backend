# API Gateway stage
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.login_api.id
  name        = "$default"
  auto_deploy = true
  
  default_route_settings {
    throttling_rate_limit  = 100
    throttling_burst_limit = 50
  }

  tags = {
    Name        = "${var.api_name}-default-stage"
    Environment = "dev"
  }
}


# Login API
resource "aws_apigatewayv2_api" "login_api" {
  name          = var.api_name
  protocol_type = "HTTP"
  description   = "API Gateway for login functionality"
  
  cors_configuration {
    allow_origins     = ["http://localhost:4200"]
    allow_credentials = true
    allow_methods     = ["POST", "GET", "OPTIONS"]
    allow_headers     = ["content-type", "authorization"]
    max_age          = 86400
  }

  tags = {
    Name        = var.api_name
    Environment = "dev"
  }
}

# What is this?
resource "aws_apigatewayv2_integration" "login_lambda_integration" {
  api_id             = aws_apigatewayv2_api.login_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.login_lambda.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
  timeout_milliseconds = 30000
}

# Login endpoint
resource "aws_apigatewayv2_route" "login_post" {
  api_id    = aws_apigatewayv2_api.login_api.id
  route_key = "POST /login"
  target    = "integrations/${aws_apigatewayv2_integration.login_lambda_integration.id}"
}

# Log back in endpoint
resource "aws_apigatewayv2_route" "login_get" {
  api_id    = aws_apigatewayv2_api.login_api.id
  route_key = "GET /login"
  target    = "integrations/${aws_apigatewayv2_integration.login_lambda_integration.id}"
}

# CORS preflight for login endpoint
resource "aws_apigatewayv2_route" "login_options" {
  api_id    = aws_apigatewayv2_api.login_api.id
  route_key = "OPTIONS /login"
  target    = "integrations/${aws_apigatewayv2_integration.login_lambda_integration.id}"
}

# Lambda Permissions for Login
resource "aws_lambda_permission" "allow_api_gateway_login" {
  statement_id  = "AllowAPIGatewayInvokeLogin"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.login_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.login_api.execution_arn}/*/*"
}