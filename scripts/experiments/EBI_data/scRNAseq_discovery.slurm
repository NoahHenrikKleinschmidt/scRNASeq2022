#!/bin/bash

#SBATCH --job-name="EcoTyp-scRNA-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=20
#SBATCH --mem=200G
#SBATCH --time=50:00:00

# NOTE: It really requires A LOOOOT of memory! They state 50+ but at 100 I get a memory error. Now let's check at 200...

# This script performs EcoTyper Ecotype Discovery on the scRNA-seq dataset (from EBI)

conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/scRNA"
scripts="${parent}/scRNASeq2022/scripts"
ecotyper="${parent}/ecotyper"

cd $ecotyper

# the data contains a normalised counts matrix in MatrixArchive format which we have to convert from .mtx to a regular tsv file
# the data was normalised to CPM using scanpy (scanpy is really cool...)

filename="${data}/resources/scExpressionAtlass/E-HCAD-9/E-HCAD-9.aggregated_filtered_normalised_counts"
file="${filename}.tsv"

# if we need to convert the file to TSV then do so
if [ ! -f "${file}" ]; then
    
    echo "Converting to TSV..."
    mtx="${filename}.mtx"
    mtx_to_tsv --names "${mtx}"

fi

# now run EcoTyper
echo "Running EcoTyper..."
config="${scripts}/experiments/EBI_data/scRNAseq_discovery.yml"
Rscript $ecotyper/EcoTyper_discovery_scRNA.R -c "${config}"

