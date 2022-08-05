"""
This script allows normalisation of raw counts from an expression matrix (countTable) column-wise to TPM.
"""

import argparse
import tpm_handler.core as core

def setup_cli():
    """
    Sets up the command line interface consisting of two commands:

    - compute-length | computes the lengths of the features from a GTF file
    - normalise | normalises the counts in a countTable to TPM using the lengths from a GTF file computed before.
    """
    descr = "Normalise counts of an expression matrix (countTable) column-wise to TPM."
    parser = argparse.ArgumentParser( description = descr )
    cmd_parser = parser.add_subparsers( dest = "command" )

    length_measure = cmd_parser.add_parser( "compute-length", help = "Compute the length of gene features based on a GTF file using gtftools." )
    length_measure.add_argument( "file", help = "The GTF file containing all gene features." )
    length_measure.add_argument( "-o", "--output", help = "The output file.", default = None )
    length_measure.add_argument( "-m", "--mode", help = "The mode of the computation. The default is 'l'.", default = "l" )
    length_measure.add_argument( "-n", "--add_names", help = "Also add a column with gene names (will be 2nd column)", action = "store_true" )

    convert_tpm = cmd_parser.add_parser( "normalise", help = "Convert counts to TPM." )
    convert_tpm.add_argument( "file", help = "The input count table in TSV format." )
    convert_tpm.add_argument( "-o", "--output", help = "The output file.", default = None )
    convert_tpm.add_argument( "-l", "--lengths", help = "The file containing the lengths of the features." )
    convert_tpm.add_argument( "-r", "--round", type = int, help = "The number of decimals to round the TPM values to.", default = 0 )
    convert_tpm.add_argument( "-n", "--use_names", help = "Store the gene_names instead of gene_ids in the first column (only works if gene_names are in the lengths file). Note: this does not affect the name of the first column, only its contents!", action = "store_true" )
    return parser

def main():
    """
    The main function
    """
    parser = setup_cli()
    args = parser.parse_args()

    if args.command == "compute-length":
        if args.output is None:
            outfile = args.file.replace( ".gtf", ".lengths" )
        else:
            outfile = args.output
        core.call_gtftools( args.file, outfile, mode = args.mode )
        if args.add_names:
            core.add_gtf_gene_names( args.file, outfile )

    elif args.command == "normalise":
        table = core.Table( args.file )
        table.set_lengths( args.lengths )
        table.normalise( args.round )
        if args.output is None:
            outfile = f"{ args.file.split('.')[0] }.tpm"
        else:
            outfile = args.output
        table.save( outfile, use_names = args.use_names ) 
    else:
        parser.print_help()
        exit( 1 )


if __name__ == "__main__":
   main()