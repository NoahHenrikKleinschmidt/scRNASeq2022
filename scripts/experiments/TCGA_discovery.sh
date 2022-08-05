#!/bin/bash

#SBATCH --job-name="EcoTyp-TCGA-discovery"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=08:00:00
#SBATCH --mem-per-cpu=50G

# This script performs EcoTyper Ecotype Discovery on the TCGA dataset (bulk-RNA-seq)

--------------------------------------------------------------------------------

NOTE:
We delay this part a bit since we don't yet have a token for running CIBERSORTx ... 

--------------------------------------------------------------------------------


conda activate EcoTyper

parent="/data/users/${USER}/EcoTyper"
data="${parent}/data/bulk"
scripts="${parent}/scRNASeq2022/scripts"
TCGA="${data}/TCGA_data"
ecotyper="${parent}/ecotyper"

# convert the data to normalised if not yet done
tpm_data="${TCGA}/samples_all.tpm"

if [ ! -f $tpm_data ]; then

    lengths="${data}/gencode.v22.annotation.genelength"
    counts="${TCGA}/all_samples.countTable"

    tpm_handler normalise -r 5 -l $lengths $counts

fi

# now run EcoTyper

Rscript $ecotyper/

