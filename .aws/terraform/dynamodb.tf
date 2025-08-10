module "user_table" {
  source        = "./impl/dynamodb"
  table_name    = "users-dev"
  partition_key = "user_id"
  sort_key      = "email"
  environment   = "dev"
}