resource "aws_lambda_function" "template_lambda" {
  function_name = var.lambda_name
  role          = var.existing_iam_role_arn
  handler       = "main.lambda_handler"
  runtime       = "python3.11"
  filename      = var.lambda_filename
  layers        = var.lambda_layers
  timeout       = 30
  memory_size   = 128
}