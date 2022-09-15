#!/bin/bash

#SBATCH --job-name="EcoTyp-scRNA-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=30
#SBATCH --mem=200G
#SBATCH --time=80:00:00
#SBATCH --output=our_own_disc2.out

# NOTE: It really requires A LOOOOT of memory! They state 50+ but at 100 I get a memory error. Now let's check at 200...
# NOTE: This now uses the NEW ecotyper version they uploaded after my issues...


conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/scRNA/merged_seurat"
scripts="${parent}/scRNASeq2022/scripts"
ecotyper="${parent}/ecotyper_new"
base_lib64="${parent}/ecotyper_new/lib64"

LD_LIBRARY_PATH=$base_lib64

cd $ecotyper

# load the config file for the experiment
config="${scripts}/experiments/our_data/scRNAseq_discovery.yml"

# now run EcoTyper
echo "Running EcoTyper..."
Rscript $ecotyper/EcoTyper_discovery_scRNA.R -c "${config}"

