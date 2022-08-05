# https://www.biostars.org/p/307603/
# I calculated the total lenght of non-overlapping exons for each gene: /home/andrej/Data/Projects/Melanoma_Quentin/GDC_data/gencode.v22.annotation.gtf.genelength
# Convert counts to transcripts per million (TPM).
#############################################################################################################
# Simplified function
#' @param counts A numeric matrix of raw feature counts i.e. fragments assigned to each gene.
#' @param featureLength A numeric vector with feature lengths.
#' @return tpm A numeric matrix normalized by library size and feature length.
Counts_to_tpm <- function(counts, featureLength) {

  # Ensure valid arguments.
  stopifnot(length(featureLength) == nrow(counts))

  # Compute effective lengths of features in each library.
  effLen <- featureLength

  # Process one column at a time.
  tpm <- do.call(cbind, lapply(1:ncol(counts), function(i) {
    rate = log(counts[,i]) - log(effLen)
    denom = log(sum(exp(rate)))
    exp(rate - denom + log(1e6))
  }))

  # Copy the row and column names from the original matrix.
  colnames(tpm) <- colnames(counts)
  rownames(tpm) <- rownames(counts)
  return(tpm)
}
#############################################################################################################

counts <- read.csv("samples_all.countTable", header=TRUE, sep="\t", row.names = 1)
gene_lengths <- read.csv("../gencode.v22.annotation.genelength", header=TRUE, sep="\t", row.names = 1)
# Keep only merged lengths
gene_lengths <- gene_lengths[c("merged")]

# Merge counts and lengths (keep the same order as in counts, keep rownames as is)
counts_lengths <- transform(merge(counts, gene_lengths, by=0), row.names=Row.names, Row.names=NULL)
# Move 'merged' column in front for clarity
counts_lengths <- counts_lengths[,c(ncol(counts_lengths),1:(ncol(counts_lengths)-1))]

# Get TPMs from our counts
TPMs <- Counts_to_tpm(counts_lengths[,-1],counts_lengths$merged)

# Save the table
# To save rownames with a header, add rownames as 1st column ('tibble').
# Too many digits makes the output file very large (exceding 500 MB limit in Cibersort). 5 decimal points should be enough ('dplyr').
library('tibble')
library('dplyr')
write.table(rownames_to_column(as.data.frame(TPMs),'geneID') %>% mutate_if(is.numeric, round, digits = 5),file="samples_all.countTable.TPM", sep="\t", quote = FALSE, row.names=FALSE)

# Replace ensembl codes with gene symbols:
gene_names <- read.csv("../gencode.v22.annotation.gene.info", header=TRUE, sep="\t", colClasses=c("NULL", "NULL", "NULL", "NULL", NA, "NULL", NA), row.names = 5)

# Merge TPMs and gene names (keep the same order as in TPMs, keep rownames as is)
TPMs_gnames <- transform(merge(TPMs, gene_names, by=0), row.names=Row.names, Row.names=NULL)
# Move 'gene_name' column in front for clarity
TPMs_gnames <- TPMs_gnames[,c(ncol(TPMs_gnames),1:(ncol(TPMs_gnames)-1))]

# A problem with gene names is that there are duplicate names. See https://bioinformatics.stackexchange.com/questions/2959/duplicate-genes-with-rsem-counts-which-one-to-choose
# The best is to sum duplicate genes.
TPMs_gnames <- aggregate(. ~ gene_name, TPMs_gnames, sum) # see https://stackoverflow.com/questions/1660124/how-to-sum-a-variable-by-group
# Save to file
write.table(TPMs_gnames %>% mutate_if(is.numeric, round, digits = 5),file="samples_all.countTable.TPM.gnames_sum_dup", sep="\t", quote = FALSE, row.names=FALSE)

#################################################
# Do the same for the protien_coding table

counts.protein_coding <- read.csv("samples_all.protein_coding.countTable", header=TRUE, sep="\t", row.names = 1)
gene_lengths.protein_coding <- read.csv("../gencode.v22.annotation.protein_coding.genelength", header=TRUE, sep="\t", row.names = 1)
# Keep only merged lengths
gene_lengths.protein_coding <- gene_lengths.protein_coding[c("merged")]

# Merge counts and lengths (keep the same order as in counts, keep rownames as is)
counts_lengths.protein_coding <- transform(merge(counts.protein_coding, gene_lengths.protein_coding, by=0), row.names=Row.names, Row.names=NULL)
# Move 'merged' column in front for clarity
counts_lengths.protein_coding <- counts_lengths.protein_coding[,c(ncol(counts_lengths.protein_coding),1:(ncol(counts_lengths.protein_coding)-1))]

# Get TPMs from our counts
TPMs.protein_coding <- Counts_to_tpm(counts_lengths.protein_coding[,-1],counts_lengths.protein_coding$merged)

# Save the table
# To save rownames with a header, add rownames as 1st column ('tibble').
# Too many digits makes the output file very large (exceding 500 MB limit in Cibersort). 5 decimal points should be enough ('dplyr').
library('tibble')
library('dplyr')
write.table(rownames_to_column(as.data.frame(TPMs.protein_coding),'geneID') %>% mutate_if(is.numeric, round, digits = 5),file="samples_all.protein_coding.countTable.TPM", sep="\t", quote = FALSE, row.names=FALSE)

# Replace ensembl codes with gene symbols:
# Merge TPMs and gene names (keep the same order as in TPMs, keep rownames as is)
TPMs.protein_coding_gnames <- transform(merge(TPMs.protein_coding, gene_names, by=0), row.names=Row.names, Row.names=NULL)
# Move 'gene_name' column in front for clarity
TPMs.protein_coding_gnames <- TPMs.protein_coding_gnames[,c(ncol(TPMs.protein_coding_gnames),1:(ncol(TPMs.protein_coding_gnames)-1))]

# A problem with gene names is that there are duplicate names. See https://bioinformatics.stackexchange.com/questions/2959/duplicate-genes-with-rsem-counts-which-one-to-choose
# The best is to sum duplicate genes.
TPMs.protein_coding_gnames <- aggregate(. ~ gene_name, TPMs.protein_coding_gnames, sum) # see https://stackoverflow.com/questions/1660124/how-to-sum-a-variable-by-group
# Save to file
write.table(TPMs.protein_coding_gnames %>% mutate_if(is.numeric, round, digits = 5),file="samples_all.protein_coding.countTable.TPM.gnames_sum_dup", sep="\t", quote = FALSE, row.names=FALSE)
