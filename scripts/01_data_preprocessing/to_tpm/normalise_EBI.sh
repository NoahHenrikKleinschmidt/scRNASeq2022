#!/bin/bash
#
# This script will convert raw countTable values to TPM using tpm_handler (defined in the scripts folder and should have been installed during setup).
#

# setup some directory variables
parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/bulk"
gtf="${parent}/gtf"
gtf_version="22" # can be any GTF version that is stored as a gtf file in the gtf directory

# ----------------------------------------------------------------
# start with the TCGA data
# ----------------------------------------------------------------
lengths="${data}/gencode.v${gtf_version}.annotation.genelength"

# NOTE: Something is weird with this length file. Somehow the data always ends up as NaNs...
# this could be a problem with the GTF version 22 which might be a different subversion or something.
# The method itself used to generate it should be the same as for the genelength file provided. I think.
# Anyway, we will use the provided file since this one works...

# lengths="${gtf}/gencode.v${gtf_version}.annotation.lengths"
# compute the lengths if they have not yet been computed...
# this new file differs from the one provided only in that it 
# already includes the gene names in column 2
# if [ ! -f "$lengths" ]; then
#     gtf_file="${gtf}/gencode.v${gtf_version}.annotation.gtf"
#     tpm_handler compute-length $gtf_file
# fi

file="${data}/TCGA_data/samples_all.countTable"
tpm_handler normalise -l $lengths -r 5 $file