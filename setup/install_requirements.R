# This script will install the required packages
# as specified on the EcoTyper GitHub page.

if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

BiocManager::install("ComplexHeatmap")
BiocManager::install("Biobase")


options( install.packages.check.source = "no" )

packages = c(

                # these are for working with the provided rds data
                "Seurat",

                # all of these are for EcoTyper
                "config",
                "ggplot2",
                "NMF",
                "RColorBrewer",
                "cluster",
                "circlize",
                "cowplot",
                "doParallel",
                "reshape2",
                "viridis",
                "argparse",
                "colorspace",
                "plyr",
                "dplyr",
                "stringr",
                "data.table",
                "matrixTests",
                "ncdf4",
                "HiClimR"
            )

chooseCRANmirror( ind = 41 )
install.packages( packages ) 
