#!/bin/bash

#SBATCH --job-name="EcoTyp-scRNA-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=30
#SBATCH --mem=200G
#SBATCH --time=80:00:00
#SBATCH --output=hepato_to_stellate_run2.out

# NOTE: This script tests dropping the hepatoblasts entirely from the dataset. 
#       And inspect the inpact on the outcome of EcoTyper results.

# This script performs EcoTyper Ecotype Discovery on the scRNA-seq dataset.

conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/scRNA/merged_seurat"
scripts="${parent}/scRNASeq2022/scripts"
ecotyper="${parent}/ecotyper"

cd $ecotyper

# load the config file for the experiment
config="${scripts}/experiments/our_data/hepato_to_stellate.yml"

# now run EcoTyper
echo "Running EcoTyper..."
Rscript $ecotyper/EcoTyper_discovery_scRNA.R -c "${config}"

