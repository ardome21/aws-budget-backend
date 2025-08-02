#!/bin/bash
set -e

echo "Building Plaid Lambda Layer..."

# Build Docker image
docker build -t plaid-layer .

# Create container and extract zip
docker create --name temp-plaid-layer plaid-layer
docker cp temp-plaid-layer:/plaid_layer.zip ./plaid_layer.zip
docker rm temp-plaid-layer

echo "Layer built successfully: plaid_layer.zip"
echo "Size: $(du -h plaid_layer.zip | cut -f1)"