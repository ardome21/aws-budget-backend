resource "aws_lambda_layer_version" "jwt_layer" {
  layer_name          = "jwt-layer"
  description         = "Bcrypt library for password hashing"
  compatible_runtimes = ["python3.11"]
  filename            = "../../layers/jwt_layer.zip"
  source_code_hash = filebase64sha256("../../layers/jwt_layer.zip")
}
