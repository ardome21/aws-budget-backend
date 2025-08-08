module "auth_api" {
  source   = "./impl/apigateway"
  api_name = "auth-api"

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
    }
    ,
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
    }
  ]
}
