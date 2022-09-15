#!/bin/bash

# This script performs gene set enrichment using eco_helper on provided 
# results directories.

# ---------------------------------------------------------------------
# Accepted arguments:
#  directory    directory containing EcoTyper results to analyze. 
#               This must be the basename of a subdirectory of the 
#               within the results directory.
#
# nb_config     the notebook config file. If this is not provided, no 
#               notebook will be generated.
# ---------------------------------------------------------------------

#SBATCH --job-name="gsea-enrich"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --time=01:00:00
#SBATCH --output="gsea-enrich-%j.out"

conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
scripts="${parent}/scripts/experiments/gene_set_enrichment"
results="${parent}/results"
outdir="${parent}/gsea_enrichment"

gene_sets="Reactome_2016 WikiPathway_2021_Human Panther_2016 GO_Biological_Process_2021 GO_Molecular_Function_2021 GO_Cellular_Component_2021"

directory=$1
notebook_config=$2

if [ $directory == "" ]; then
    echo "No directory provided. Make sure to provide one subdirectory within"
    echo $results
    exit 1
fi

if [ ! -d "${outdir}" ]; then
    mkdir -p ${outdir}
fi


eco_helper enrich --enrichr --assemble --gene_sets $gene_sets --output "${outdir}/${directory}" "${results}/${directory}"

if [ ! $notebook_config == "" ]; then
    eco_helper enrich --notebook --notebook_config $notebook_config "${scripts}/${directory}_enrichment.ipynb"
fi

