terraform {
  backend "s3" {
    bucket         = "budget-terraform-state-dev"
    key            = "lambda-api/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "budget-terraform-state-lock"
  }
}
