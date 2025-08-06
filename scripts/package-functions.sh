#!/bin/bash
set -e

# Create build directory
mkdir -p build/functions

# Function to package a single Lambda function
package_function() {
    local func_name=$1
    local func_dir="lambdas/${func_name}"
    
    if [ ! -d "$func_dir" ]; then
        echo "Function directory $func_dir not found"
        return 1
    fi
    
    echo "Packaging function: $func_name"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    local zip_file="build/functions/${func_name}.zip"
    
    # Copy function code
    cp -r "$func_dir"/* "$temp_dir/"
    
    # Install dependencies if requirements.txt exists
    if [ -f "$func_dir/requirements.txt" ]; then
        echo "Installing dependencies for $func_name"
        pip install -r "$func_dir/requirements.txt" -t "$temp_dir" --quiet
    fi
    
    # Create zip file
    cd "$temp_dir"
    zip -r "$(pwd)/../$zip_file" . -q
    cd - > /dev/null
    
    # Clean up
    rm -rf "$temp_dir"
    
    echo "Packaged $func_name -> $zip_file"
}

# Package specific function if provided, otherwise package all
if [ $# -eq 1 ]; then
    package_function "$1"
else
    # Package all functions
    for func_dir in lambdas/*/; do
        if [ -d "$func_dir" ]; then
            func_name=$(basename "$func_dir")
            package_function "$func_name"
        fi
    done
fi

echo "Function packaging complete!"