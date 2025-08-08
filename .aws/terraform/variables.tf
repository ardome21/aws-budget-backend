variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "existing_iam_role_arn" {
  description = "ARN of the existing IAM role to use for Lambda"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the login Lambda function"
  type        = string
  default     = "login-function-deployed"
}

variable "api_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "login-api-deploy"
}
