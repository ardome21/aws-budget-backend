variable "table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "partition_key" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
}