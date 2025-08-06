# Lambda Layers
resource "aws_lambda_layer_version" "layers" {
  for_each = var.lambda_layers

  layer_name          = "${var.project_name}-${var.environment}-${each.key}"
  filename            = "../build/layers/${each.key}.zip"
  compatible_runtimes = each.value.compatible_runtimes
  description         = each.value.description

  depends_on = [null_resource.build_layers]
}

# Trigger to rebuild layers when source changes
resource "null_resource" "build_layers" {
  triggers = {
    # This will trigger rebuild when the build script changes
    build_script_hash = filebase64sha256("../scripts/build-layers.sh")
    
    # Add trigger for when layer source files change
    layers_timestamp = timestamp()
  }

  provisioner "local-exec" {
    command = "cd .. && ./scripts/build-layers.sh"
  }
}