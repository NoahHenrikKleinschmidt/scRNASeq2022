#!/usr/bin/bash

# This is the the slurm wrapper for the normalisation script for our data.

#SBATCH --job-name="normalise_our"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=50G
#SBATCH --time=10:00:00

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

# and while we're at it also vet the columns to make them conformant to EcoTyper requirements
# and save the final (vetted) files to a dedicated subfolder "ecotyper_friendly"
fix_annotations -p -o "${data}/ecotyper_friendly/" $data