#!/bin/bash

# This script expect 4 arguments:
# 1) A temp folder with the signature file in it, the association file, the model file, and the matrix
# 2) Signature name
# 3) TSX_ID
# 4) Result dir

set -e

# Source env first

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -lt 4 ]
  then
    echo "Less than four argument supplied. Stopping.."
    exit 1
fi

TEMP_DIR="$1"
SIG_NAME="$2"
SIG_ID="$3"
RESULT_DIR="$4"
SIG_FULL_NAME="$SIG_ID $SIG_NAME"

. /opt/conda/etc/profile.d/conda.sh
conda activate condaR_TCL

Rscript "$CURRENT_DIR""/STEP2_predict_modif.R" "$SIG_FULL_NAME" "$TEMP_DIR""$SIG_ID.sign" "$TEMP_DIR""mat_chempsy_final_10793.tsv" "$TEMP_DIR""model.h5" "$TEMP_DIR""association_matrix.tsv" "$TEMP_DIR"

cp "$TEMP_DIR""prediction_results.tsv" "$RESULT_DIR"
#rm -rf "$TEMP_DIR"
