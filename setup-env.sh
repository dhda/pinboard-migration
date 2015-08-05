#!/bin/bash

set -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

ENV_NAME="env"

# Setup Python environment (requires python3)
cd $DIR
pyvenv $ENV_NAME
source $ENV_NAME/bin/activate

pip install --upgrade pip
pip install --upgrade ipython requests pocket toml

echo "Successfully set up Python environment. To use it, run:"
echo "source $DIR/$ENV_NAME/bin/activate"
