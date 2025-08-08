module "login_lambda" {
  source          = "./impl/lambda"
  lambda_name     = "login_lambda"
  lambda_handler  = "login.handler"
  lambda_filename = "login.zip"
  lambda_layers   = [aws_lambda_layer_version.jwt_layer.arn]
}