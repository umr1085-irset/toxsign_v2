#!/bin/bash

# This script
# 1) Input folder with sign.tss file, + method.RData
# 3) Output file with full path

set -e

# Source env first

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -lt 2 ]
  then
    echo "Less than tree argument supplied. Stopping.."
    exit 1
fi

TEMP_DIR="$1"
OUTPUT_DIR="$2"

. /opt/conda/etc/profile.d/conda.sh
conda activate condaR_TCL

Rscript ./prepare_clustering_method.R "$TEMP_DIR""TSS.sign" "$TEMP_DIR""method.RData" "$TEMP_DIR"

cp "$TEMP_DIR""output.txt" "$OUTPUT_DIR"

rm -rf "$TEMP_DIR"
