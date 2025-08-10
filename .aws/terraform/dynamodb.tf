module "user_table" {
  source        = "./impl/dynamodb"
  table_name    = "users-dev"
  partition_key = "user_id"
  secondary_index_key = "email"
  environment   = "dev"
}

module "plaid_connections_table" {
  source        = "./impl/dynamodb"
  table_name    = "plaid-connections-dev"
  partition_key = "user_id"
  sort_key      = "item_id"
  secondary_index_key = "email"
  environment   = "dev"
}