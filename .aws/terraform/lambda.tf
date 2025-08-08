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

  module "verify_account_lambda" {
  source               = "./impl/lambda"
  lambda_name          = "verify-account-dev"
  source_file          = "../../lambdas/auth/VerifyAccount/main.py"
  existing_iam_role_arn = var.existing_iam_role_arn
  lambda_layers         = [aws_lambda_layer_version.jwt_layer.arn]
}

  module "plaid_create_link_lambda" {
  source               = "./impl/lambda"
  lambda_name          = "plaid-create-link-dev"
  source_file          = "../../lambdas/plaid/CreateLink/main.py"
  existing_iam_role_arn = var.existing_iam_role_arn
  lambda_layers         = [aws_lambda_layer_version.plaid_layer.arn]
}

  module "plaid_exchange_token_lambda" {
  source               = "./impl/lambda"
  lambda_name          = "plaid-exchange-token-dev"
  source_file          = "../../lambdas/plaid/ExchangeToken/main.py"
  existing_iam_role_arn = var.existing_iam_role_arn
  lambda_layers         = [aws_lambda_layer_version.plaid_layer.arn]
}

module "plaid_get_account_details_lambda" {
  source               = "./impl/lambda"
  lambda_name          = "plaid-get-account-details-dev"
  source_file          = "../../lambdas/plaid/GetAccountDetails/main.py"
  existing_iam_role_arn = var.existing_iam_role_arn
  lambda_layers         = [aws_lambda_layer_version.plaid_layer.arn]
}