variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "lambda_functions" {
  description = "Configuration for Lambda functions"
  type = map(object({
    handler     = string
    runtime     = string
    timeout     = number
    memory_size = number
    layers      = list(string)
    environment_variables = map(string)
    api_gateway = object({
      path   = string
      method = string
    })
  }))
  default = {}
}

variable "lambda_layers" {
  description = "Configuration for Lambda layers"
  type = map(object({
    description = string
    compatible_runtimes = list(string)
  }))
  default = {}
}