#!/bin/bash

# This script expect at least two arguments:
# 1) A temp folder with the signature file and the homolog file
# 2) A results folder
# 3) A path to the signature to be compared

set -e

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

# Prepare enrichment

wish8.6 "$CURRENT_DIR""/prepare_enrichment.tcl" \
    -hg2go "$TEMP_DIR""/annotation"\
    -sign  "$SIGNATURE"\
    -o "$TEMP_DIR""signature.enr"

Rscript "$CURRENT_DIR""/compute_enrichment.R" "$TEMP_DIR""signature.enr" "$TEMP_DIR""signature.enr"

cp "$TEMP_DIR""signature.enr" "$RESULT_DIR"
rm -rf "$TEMP_DIR"
