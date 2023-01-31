# scRNA-Seq Data Analysis Project by <font style="color:DodgerBlue;">EcoTyper</font>


This project analyses scRNA-Seq data from hepatocellular carcinoma using the EcoTyper software by [Steen/Luca et al. (2021)](https://www.cell.com/cancer-cell/fulltext/S1535-6108(21)00451-7). This repository contains scripts used for data analysis and environment setup. 

# Outline

This project aims to assess the uses of EcoTyper for scRNA-seq from  Hepatcarcinoma samples. We are going to analyse scRNA-seq (15 cancer, 2 normal) liver biopsies to identify the different ecotypes in there. 

# Setup 
First, set up the environment using the `setup/setup_environment.sh` script. Once finished, activate the environment using `conda activate EcoTyper` (or whatever name you passed to the script as optional argument). 

# Data Preprocessing

Ecotyper requires TSV-formatted CPM or TPM input data not containing spaces or dashes in the sample names. Hence, some pre-processing may be necessary. The environment installs the package [eco_helper](https://github.com/NoahHenrikKleinschmidt/eco_helper) which can be used to pre-process the data. 

# Running EcoTyper

EcoTyper can be run by adjusting the configuration files in `scripts/experiments/ecotyper` and by then running the script `scripts/experiments/ecotyper/scRNAseq_discovery.slurm`. 

# GSEA analysis

[eco_helper](https://github.com/NoahHenrikKleinschmidt/eco_helper) can be used to automatically perform gene set enrichment analysis (GSEA) on the produced ecotypes. Output formats are raw files, a jupyter notebook (requiring an additional configuration file in yaml format), and/or a pickle file. The pickle file can be loaded into the [eco_helper Viewer](https://github.com/NoahHenrikKleinschmidt/eco_helper_viewer) web-app to explore GSEA results more easily. 


