module "auth_api" {
  source   = "./impl/apigateway"
  api_name = "auth-api-dev"

  routes = [
    {
      method            = "POST"
      path              = "/login"
      lambda_name       = module.login_lambda.function_name
      lambda_invoke_arn = module.login_lambda.invoke_arn
    },
    {
      method            = "GET"
      path              = "/login"
      lambda_name       = module.login_lambda.function_name
      lambda_invoke_arn = module.login_lambda.invoke_arn
    },
    {
      method            = "OPTIONS"
      path              = "/login"
      lambda_name       = module.login_lambda.function_name
      lambda_invoke_arn = module.login_lambda.invoke_arn
    },
    {
      method            = "POST"
      path              = "/logout"
      lambda_name       = module.logout_lambda.function_name
      lambda_invoke_arn = module.logout_lambda.invoke_arn
    },
    {
      method            = "OPTIONS"
      path              = "/logout"
      lambda_name       = module.logout_lambda.function_name
      lambda_invoke_arn = module.logout_lambda.invoke_arn
    },
    {
      method            = "POST"
      path              = "/verify-account"
      lambda_name       = module.verify_account_lambda.function_name
      lambda_invoke_arn = module.verify_account_lambda.invoke_arn
    },
    {
      method            = "OPTIONS"
      path              = "/verify-account"
      lambda_name       = module.verify_account_lambdafunction_name
      lambda_invoke_arn = module.lverify_account_lambda.invoke_arn
    },
  ]
}

module "plaid_api" {
  source   = "./impl/apigateway"
  api_name = "plaid-api-dev"

  routes = [
    {
      method            = "POST"
      path              = "/get-plaid-link"
      lambda_name       = module.plaid_create_link_lambda.function_name
      lambda_invoke_arn = module.plaid_create_link_lambda.invoke_arn
    },
    {
      method            = "OPTIONS"
      path              = "/get-plaid-link"
      lambda_name       = module.plaid_create_link_lambda.function_name
      lambda_invoke_arn = module.plaid_create_link_lambda.invoke_arn
    },
    {
      method            = "POST"
      path              = "/exchange-plaid-token"
      lambda_name       = module.plaid_exchange_token_lambda.function_name
      lambda_invoke_arn = module.plaid_exchange_token_lambda.invoke_arn
    },
    {
      method            = "OPTIONS"
      path              = "/exchange-plaid-token"
      lambda_name       = module.plaid_exchange_token_lambda.function_name
      lambda_invoke_arn = module.plaid_exchange_token_lambda.invoke_arn
    },
  ]
}

