#!/bin/bash

set -e
LAYER_DIR="layer/lambda_one_python"
ZIP_FILE="layer_one.zip"
REQUIREMENTS="lambda_one/requirements.txt"

rm -rf layer $ZIP_FILE

mkdir -p $LAYER_DIR

pip install -r $REQUIREMENTS -t $LAYER_DIR

cd layer
zip -r ../$ZIP_FILE .
cd ..

echo "Layer zip created: $ZIP_FILE"
