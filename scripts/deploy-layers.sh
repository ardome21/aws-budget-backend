#!/bin/bash
set -e

echo "Building Lambda layers..."

# Create build directory
mkdir -p build/layers

# Build each layer
for layer_dir in layers/*/; do
    if [ -d "$layer_dir" ]; then
        layer_name=$(basename "$layer_dir")
        echo "Building layer: $layer_name"
        
        cd "$layer_dir"
        
        if [ -f "Dockerfile" ]; then
            # Build using Docker
            docker build -t "${layer_name}-layer" .
            
            # Extract the layer zip file
            container_id=$(docker create "${layer_name}-layer")
            docker cp "${container_id}:/app/layer.zip" "../../build/layers/${layer_name}.zip"
            docker rm "${container_id}"
        else
            echo "No Dockerfile found for layer: $layer_name"
        fi
        
        cd - > /dev/null
    fi
done

echo "Layer building complete!"