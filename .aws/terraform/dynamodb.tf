module "user_table" {
  source        = "./impl/dynamodb"
  table_name    = "users-dev"
  partition_key = "email"
  sort_key      = "user_id"
  environment   = "dev"
}