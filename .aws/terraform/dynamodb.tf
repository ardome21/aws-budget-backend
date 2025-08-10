module "user_table" {
  source        = "./impl/dynamodb"
  table_name    = "users-dev"
  partition_key = "user_id"
  secondary_index_key = "email"
  environment   = "dev"
}