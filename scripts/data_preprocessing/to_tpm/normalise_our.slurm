#!bin/bash

# This is the the slurm wrapper for the normalisation script for our data.

#SBATCH --job-name="normalise_our"
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=200G
#SBATCH --time=10:00:00

bash normalise_our.sh