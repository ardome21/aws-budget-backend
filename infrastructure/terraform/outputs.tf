output "api_gateway_url" {
  description = "Base URL for API Gateway stage"
  value       = aws_api_gateway_stage.main.invoke_url
}

output "lambda_function_names" {
  description = "Names of the Lambda functions"
  value = {
    for k, v in aws_lambda_function.functions : k => v.function_name
  }
}

output "lambda_function_arns" {
  description = "ARNs of the Lambda functions"
  value = {
    for k, v in aws_lambda_function.functions : k => v.arn
  }
}

output "layer_arns" {
  description = "ARNs of the Lambda layers"
  value = {
    for k, v in aws_lambda_layer_version.layers : k => v.arn
  }
}