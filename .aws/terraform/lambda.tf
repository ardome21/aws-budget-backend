data "archive_file" "login_lambda_zip" {
  type        = "zip"
  source_file = "../../lambdas/auth/Login/lambda_function.py"
  output_path = "../../output/login_lambda.zip"
}

resource "aws_lambda_function" "login_lambda" {
  function_name = var.lambda_function_name
  role         = var.existing_iam_role_arn
  handler      = "lambda_function.lambda_handler"
  runtime      = "python3.11"
  
  filename         = data.archive_file.login_lambda_zip.output_path
  source_code_hash = data.archive_file.login_lambda_zip.output_base64sha256
  
  layers = [aws_lambda_layer_version.bcrypt_layer.arn]
  
  timeout     = 30
  memory_size = 128
  
  environment {
    variables = {
      # Add any environment variables your login function needs
      # ENVIRONMENT = "dev"
    }
  }

  tags = {
    Name        = var.lambda_function_name
    Environment = "dev"
    Function    = "authentication"
  }
}