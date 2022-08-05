#!/bin/bash

#SBATCH --job-name="EcoTyp-scRNA-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=20
#SBATCH --mem=200G
#SBATCH --time=50:00:00

# NOTE: It really requires A LOOOOT of memory! They state 50+ but at 100 I get a memory error. Now let's check at 200...

# This script performs EcoTyper Ecotype Recovery on the scRNA-seq dataset (from EBI) using the default Carcinoma setting
# in order to do this we had to alter the celltype annotations to match known celltypes within "Carcinoma". The altered labels
# do not necessarily match the originals anymore to the latter, but this is a proof-of-principle experiment to check if 
# it works so we don't worry too much about this...

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

preset="Carcinoma"
annotations="${data}/resources/scExpressionAtlass/E-HCAD-9/E-HCAD-9.annotation_defaultCarcinoma.tsv"
threads=20
out="${parent}/results/defaultCarcinoma"

Rscript $ecotyper/EcoTyper_recovery_scRNA.R -d $preset -m $file -a $annotations -t $threads -o $out

