#!/bin/bash

#SBATCH --job-name="EcoTyp-bulk-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=200G
#SBATCH --time=80:00:00
#SBATCH --output=our_bulk.out

# NOTE: It really requires A LOOOOT of memory! They state 50+ but at 100 I get a memory error. Now let's check at 200...
# NOTE: This is the crack version ...

# This script performs EcoTyper Ecotype Discovery on the bulk RNA-seq dataset from TCGA

conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/scRNA/merged_seurat"
scripts="${parent}/scRNASeq2022/scripts"
ecotyper="${parent}/ecotyper"


# set a no-limit on cache memory in hopes of avoiding the memory errors
ulimit -c unlimited -v unlimited -s unlimited -f unlimited -n unlimited -d unlimited

cd $ecotyper

# load the config file for the experiment
config="${scripts}/experiments/our_data/bulk_discovery_crck.yml"

# now run EcoTyper
echo "Running EcoTyper..."
Rscript $ecotyper/EcoTyper_discovery_bulk.R -c "${config}"

