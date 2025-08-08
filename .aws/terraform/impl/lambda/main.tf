variable "lambda_name" {}
variable "lambda_handler" {}
variable "lambda_filename" {}
variable "existing_iam_role_arn" {}
variable "lambda_layers" {
  type    = list(string)
  default = []
}

resource "aws_lambda_function" "login_lambda" {
  function_name = var.lambda_name
  role          = var.existing_iam_role_arn
  handler       = var.lambda_handler
  runtime       = "python3.11"
  filename      = var.filename
  layers        = var.lambda_layer
  timeout       = 30
  memory_size   = 128

  tags = {
    Environment = "dev"
  }
}