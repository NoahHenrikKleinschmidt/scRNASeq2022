"""
This script allows normalisation of raw counts from an expression matrix (countTable) column-wise to TPM.
"""

import argparse
import os
import fix_annotations.core as core

def setup_cli():
    """
    Sets up the command line interface
    """
    descr = "Fix annotations of expression matrices and annotation files to conform with EcoTyper's requirements."
    parser = argparse.ArgumentParser( description = descr )
    parser.add_argument( "input", help = "The input file or directory. Note, if a directory is given, then the annotation file(s) must end with '.annotation'  and the expression file(s) must end with '.count', '.countTable', or '.tpm'." )
    parser.add_argument( "-o", "--output", help = "The output directory. By default the file(s) are saved to the same path they were read from (thereby overwriting the old ones!).", default = None )
    parser.add_argument( "-f", "--format", help = "A file specifying a dictionary of characters to be replaced.", default = None )
    parser.add_argument( "-s", "--suffix", help = "A suffix to add to the output file(s).", default = None )
    parser.add_argument( "-e", "--expression", help = "Use this to mark the given file as an expression matrix even if it does not end with a default file-suffix.", action = "store_true" )
    parser.add_argument( "-a", "--annotation", help = "Use this to mark the given file as an annotation file even if it does not end with a default file-suffix.", action = "store_true" )
    parser.add_argument( "-i", "--index", help = "Use this if the 'ID' column in the annotation file(s) is the index of of the table rather than a named 'ID' column.", action = "store_true" )
    parser.add_argument( "-p", "--pseudo", help = "Use this to only pseudo-read the given expression matrix files. This is useful when the datafiles are very large to save memory.", action = "store_true" )
    return parser

def main():
    """
    The main function
    """
    parser = setup_cli()
    args = parser.parse_args()

    if args.format is not None:
        formats = core.read_formats_file( args.format )
    else:
        formats = None

    formatter = core.Formatter( formats )

    if os.path.isdir( args.input ):
        formatter.memory_saving_dir_pipe( args.input, args.output, args.suffix, id_is_index = args.index, pseudo = args.pseudo )
        return

    elif os.path.isfile( args.input ):
        if formatter._is_annotation_table_file( args.input ) or args.annotation :
            formatter.read_annotation_table( args.input, id_is_index = args.index )
            save_func = formatter.save_annotation_table
            get_func = formatter._last_annotation

        elif formatter._is_expression_matrix_file( args.input ) or args.expression :
            formatter.read_expression_matrix( args.input, pseudo = args.pseudo )
            save_func = formatter.save_expression_matrix
            get_func = formatter._last_matrix

        else:
            raise Exception( "The input file is not a valid annotation file or expression matrix file. If your file does not end with a default file-suffix, make sure to provide the appropriate flags while reading!" )

    formatter.reformat()

    if args.output:
        if os.path.isdir( args.output ):
            formatter.save_to_dir( args.output, args.suffix )
        else:
            suffix = "" if not args.suffix else args.suffix
            outfile = f"{ os.path.abspath( args.output ) }{ suffix }"        
            save_func( outfile, get_func() )
    else:
        formatter.save_to_dir( args.output, args.suffix )
        
if __name__ == "__main__":
   main()