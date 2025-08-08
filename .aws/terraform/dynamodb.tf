module "user_table" {
  source      = "./impl/dynamodb"
  table_name  = "users-dev"
  environment = "dev"
}