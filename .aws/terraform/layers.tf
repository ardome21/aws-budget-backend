resource "aws_lambda_layer_version" "bcrypt_layer" {
  layer_name          = "bcrypt-layer"
  description         = "Bcrypt library for password hashing"
  compatible_runtimes = ["python3.11"]
  filename            = "../../layers/bcrypt_layer.zip"  # Adjust path based on your repo structure
  source_code_hash = filebase64sha256("../../layers/bcrypt_layer.zip")
}
