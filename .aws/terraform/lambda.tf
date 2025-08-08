module "login_lambda" {
  source                = "./impl/lambda"
  lambda_name           = "login_lambda"
  lambda_handler        = "login.handler"
  lambda_filename       = "../../lambdas/auth/Login/lambda_function.py"
  lambda_layers         = [aws_lambda_layer_version.jwt_layer.arn]
  existing_iam_role_arn = var.existing_iam_role_arn
  }