#!/bin/bash

# This script
# 1) Path to groups folder
# 2) Temp folder with reduced data and homologene data
# 3) Output file with full path

set -e

# Source env first

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -lt 3 ]
  then
    echo "Less than tree argument supplied. Stopping.."
    exit 1
fi

GROUP_DIR="$1"
TEMP_DIR="$2"
OUTPUT="$3"

. /opt/conda/etc/profile.d/conda.sh
conda activate condaR_TCL

Rscript ./prepare_clustering_method.R "$TEMP_DIR""data.reduced.RData" "$GROUP_DIR" "$TEMP_DIR""homologene.data" "$TEMP_DIR"

cp "$TEMP_DIR""method.RData" "$OUTPUT"

rm -rf "$TEMP_DIR"
