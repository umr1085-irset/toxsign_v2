#!/bin/bash

# This script expect one argument:
# The path to a temp folder where all the signature files are stored

set -e

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -eq 0 ]
  then
    >&2 echo "A temp folder containing all public signature files is required"
    exit 1
fi

TEMP_DIR="$1"

if [ ! -d "$TEMP_DIR" ]; then
    >&2 echo "$TEMP_DIR is not a folder"
    exit 1
fi

OUTPUT_DIR="/app/tools/admin_data/"

. /opt/conda/etc/profile.d/conda.sh
conda activate condaR_TCL

Rscript "$CURRENT_DIR""/create_signmatrix4distance.R" $TEMP_DIR "public.RData.old" "$TEMP_DIR""public.RData"
cp "$TEMP_DIR""public.RData" "$OUTPUT_DIR""public.RData"
rm -rf $TEMP_DIR
