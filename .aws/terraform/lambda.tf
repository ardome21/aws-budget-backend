  module "login_lambda" {
  source               = "./impl/lambda"
  lambda_name          = "login-dev"
  source_file          = "../../lambdas/auth/Login/main.py"
  existing_iam_role_arn = var.existing_iam_role_arn
  lambda_layers         = [aws_lambda_layer_version.jwt_layer.arn]
}

  module "logout_lambda" {
  source               = "./impl/lambda"
  lambda_name          = "logout-dev"
  source_file          = "../../lambdas/auth/Logout/main.py"
  existing_iam_role_arn = var.existing_iam_role_arn
  lambda_layers         = [aws_lambda_layer_version.jwt_layer.arn]
}