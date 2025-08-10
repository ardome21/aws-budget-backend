resource "aws_dynamodb_table" "this" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = var.partition_key
  range_key      = var.sort_key

  attribute {
    name = var.partition_key
    type = "S"
  }
  attribute {
    name = var.sort_key
    type = "S"
  }
  

  tags = {
    Environment = var.environment
  }
}