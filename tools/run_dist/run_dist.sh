#!/bin/bash

# This script expect at least two arguments:
# 1) A temp folder with all the signatures in it
# 2) A results folder
# 3) A path to the signature to be compared

# Source env first

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -lt 3 ]
  then
    echo "Less than tree argument supplied. Stopping.."
    exit 1
fi

TEMP_DIR="$1"
RESULT_DIR="$2"
SIGNATURE="$3"

. /opt/conda/etc/profile.d/conda.sh
conda activate condaR_TCL


Rscript "$CURRENT_DIR""/create_signmatrix4distance.R" "$TEMP_DIR" "$TEMP_DIR""public.RData" "$TEMP_DIR""signature_matrix.RData"
Rscript "$CURRENT_DIR""/distance4signatures.R" "$SIGNATURE" "$TEMP_DIR""signature_matrix.RData" "$TEMP_DIR""signature.dist"

cp "$TEMP_DIR""signature.dist" "$RESULT_DIR"
rm -rf "$TEMP_DIR"
