#!/bin/bash

# This script
# 1) Input folder with sign.tss file, + method.RData
# 2) Signature name
# 2) Output file with full path

set -e

# Source env first

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -lt 3 ]
  then
    echo "Less than tree argument supplied. Stopping.."
    exit 1
fi

TEMP_DIR="$1"
SIG_FILE="$2"
OUTPUT_DIR="$3"

. /opt/conda/etc/profile.d/conda.sh
conda activate condaR_TCL2

Rscript "$CURRENT_DIR""/predict_group.R" "$TEMP_DIR""$SIG_FILE" "$TEMP_DIR" "$TEMP_DIR""method.RData"

cp "$TEMP_DIR""output.txt" "$OUTPUT_DIR"

#rm -rf "$TEMP_DIR"
