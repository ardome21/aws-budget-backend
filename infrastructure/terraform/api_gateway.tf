# API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-${var.environment}-api"
  description = "API Gateway for ${var.project_name} ${var.environment}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resources and Methods
resource "aws_api_gateway_resource" "function_resources" {
  for_each = var.lambda_functions

  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = trimprefix(each.value.api_gateway.path, "/")
}

resource "aws_api_gateway_method" "function_methods" {
  for_each = var.lambda_functions

  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.function_resources[each.key].id
  http_method   = each.value.api_gateway.method
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "function_integrations" {
  for_each = var.lambda_functions

  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.function_resources[each.key].id
  http_method = aws_api_gateway_method.function_methods[each.key].http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.functions[each.key].invoke_arn
}

resource "aws_api_gateway_method_response" "function_responses" {
  for_each = var.lambda_functions

  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.function_resources[each.key].id
  http_method = aws_api_gateway_method.function_methods[each.key].http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "function_integration_responses" {
  for_each = var.lambda_functions

  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.function_resources[each.key].id
  http_method = aws_api_gateway_method.function_methods[each.key].http_method
  status_code = aws_api_gateway_method_response.function_responses[each.key].status_code

  depends_on = [aws_api_gateway_integration.function_integrations]
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  depends_on = [
    aws_api_gateway_method.function_methods,
    aws_api_gateway_integration.function_integrations,
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.function_resources,
      aws_api_gateway_method.function_methods,
      aws_api_gateway_integration.function_integrations,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.environment
}