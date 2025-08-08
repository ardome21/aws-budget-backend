terraform {
  backend "s3" {
    bucket         = "8386-budget-terraform-state"
    key            = "lambda-api/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "budget-terraform-locks"
  }
}
