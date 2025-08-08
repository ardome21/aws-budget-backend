data "archive_file" "login_lambda_zip" {
  type        = "zip"
  source_file = "../../lambda/auth/Login/lambda_function.py"  # Adjust path to your login Python script
  output_path = "../../output/login_lambda.zip"
}

resource "aws_lambda_function" "login_lambda" {
  function_name = var.lambda_function_name
  role         = var.existing_iam_role_arn
  handler      = "login.handler"  # Assuming your function is named 'handler' in login.py
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