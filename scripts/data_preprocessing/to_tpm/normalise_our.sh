#!/bin/bash
#
# This script will convert raw countTable values to TPM using tpm_handler (defined in the scripts folder and should have been installed during setup).
#

# setup some directory variables
parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/scRNA/merged_seurat"
gtf="${parent}/gtf"
gtf_version="22" # can be any GTF version that is stored as a gtf file in the gtf directory

# ----------------------------------------------------------------
# start with the TCGA data
# ----------------------------------------------------------------
# lengths="${parent}/data/bulk/gencode.v${gtf_version}.annotation.genelength"
lengths="${gtf}/v${gtf_version}.lengths"

# compute the lengths if they have not yet been computed...
# this new file differs from the one provided only in that it 
# already includes the gene names in column 2
if [ ! -f "$lengths" ]; then
    gtf_file="${gtf}/gencode.v${gtf_version}.annotation.gtf"
    tpm_handler compute-length -o $lengths -n -s $gtf_file
fi

file="${data}/merged.seurat.rds.counts.tsv"
tpm_handler normalise -l $lengths -r 5 $file