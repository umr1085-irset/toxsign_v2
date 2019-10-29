#!/bin/bash

    ADMIN_DIR="/app/tools/admin_data/"
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )""/"
    cd $ADMIN_DIR
    mkdir -p tmp
    TEMP_DIR="$ADMIN_DIR""tmp/"

    . /opt/conda/etc/profile.d/conda.sh
    conda activate condaR_TCL

    wish8.6 "$SCRIPT_DIR""homologene2go.tcl" \
        -hg "$ADMIN_DIR""homologene.data" \
        -gene2go "$ADMIN_DIR""gene2go" \
        -goobo "$ADMIN_DIR""gene_ontology.obo" \
        -o "$TEMP_DIR"

    wish8.6 "$SCRIPT_DIR""homologene2hpo.tcl" \
        -hg "$ADMIN_DIR""homologene.data" \
        -gene2hpo "$ADMIN_DIR""ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt" \
        -hpoobo  "$ADMIN_DIR""hp.obo" \
        -o "$TEMP_DIR"

    wish8.6 "$SCRIPT_DIR""homologene2mpo.tcl" \
        -hg "$ADMIN_DIR""homologene.data" \
        -gene2mgi "$ADMIN_DIR""MGI_Gene_Model_Coord.rpt" \
        -mgi2mpo "$ADMIN_DIR""MGI_PhenoGenoMP.rpt" \
        -mpoobo "$ADMIN_DIR""MPheno_OBO.ontology" \
        -o "$TEMP_DIR"

    rm -f "$ADMIN_DIR""annotation"
    touch "$ADMIN_DIR""annotation"

    cat "$TEMP_DIR""homologene2go" >> "$ADMIN_DIR""annotation"
    cat "$TEMP_DIR""homologene2mpo" >> "$ADMIN_DIR""annotation"
    cat "$TEMP_DIR""homologene2hpo" >> "$ADMIN_DIR""annotation"

    rm -rf "$ADMIN_DIR""tmp/"
