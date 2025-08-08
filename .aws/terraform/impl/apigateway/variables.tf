variable "api_name" {}
variable "routes" {
  description = "List of route definitions"
  type = list(object({
    method        = string
    path          = string
    lambda_invoke_arn = string
    lambda_name   = string
  }))
}