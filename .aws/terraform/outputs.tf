output "login_api_url" {
  description = "URL of the login API"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/login"
}

output "api_gateway_full_url" {
  description = "Full URL of the API Gateway"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "login_lambda_function_name" {
  description = "Name of the login Lambda function"
  value       = aws_lambda_function.login_lambda.function_name
}

output "login_lambda_function_arn" {
  description = "ARN of the login Lambda function"
  value       = aws_lambda_function.login_lambda.arn
}

output "jwt_layer_arn" {
  description = "ARN of the jwt layer"
  value       = aws_lambda_layer_version.jwt_layer.arn
}