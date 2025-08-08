output "user_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.user_table.name
}

output "user_table_arn" {
  description = "The ARN of the DynamoDB table"
  value       = aws_dynamodb_table.user_table.arn
}
