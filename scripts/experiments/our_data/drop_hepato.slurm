#!/bin/bash

#SBATCH --job-name="EcoTyp-scRNA-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --mem=200G
#SBATCH --time=80:00:00
#SBATCH --output=drop_hepato_run3_50.out

# NOTE: This script tests out merging the Hepatoblasts that failed at step 8 with the Hepatic stellate cells.
#       This is a good way to test out the effect of the stellate cells on the results. 
#       I predict that now the stellate cells should be a problem if the bug cause is in the data...

# This script performs EcoTyper Ecotype Discovery on the scRNA-seq dataset.

conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/scRNA/merged_seurat"
scripts="${parent}/scRNASeq2022/scripts"
ecotyper="${parent}/ecotyper"

cd $ecotyper

# load the config file for the experiment
config="${scripts}/experiments/our_data/drop_hepato.yml"

# now run EcoTyper
echo "Running EcoTyper..."
Rscript $ecotyper/EcoTyper_discovery_scRNA.R -c "${config}"

