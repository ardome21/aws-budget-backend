resource "aws_apigatewayv2_api" "login_api" {
  name          = var.api_name
  protocol_type = "HTTP"
  description   = "API Gateway for login functionality"
  
  cors_configuration {
    allow_origins     = ["*"]  # Restrict this in production
    allow_methods     = ["POST", "OPTIONS"]
    allow_headers     = ["content-type", "authorization"]
    max_age          = 86400
  }

  tags = {
    Name        = var.api_name
    Environment = "production"
  }
}

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

# CORS preflight for login endpoint
resource "aws_apigatewayv2_route" "login_options" {
  api_id    = aws_apigatewayv2_api.login_api.id
  route_key = "OPTIONS /login"
  target    = "integrations/${aws_apigatewayv2_integration.login_lambda_integration.id}"
}

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
    Environment = "production"
  }
}

resource "aws_lambda_permission" "allow_api_gateway_login" {
  statement_id  = "AllowAPIGatewayInvokeLogin"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.login_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.login_api.execution_arn}/*/*"
}