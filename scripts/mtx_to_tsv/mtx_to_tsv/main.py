"""
This script allows conversion of mtx files to tsv.
"""

import argparse
import subprocess
import os
import logging

logger = logging.getLogger( __name__ )
logger.setLevel( logging.INFO )
logger.addHandler( logging.StreamHandler() )

from .core import *

def setup_cli():
    """
    Sets up the command line interface
    """
    descr = "Convert an mtx file to tsv format."
    parser = argparse.ArgumentParser( description = descr )

    parser.add_argument( "file", help = "The mtx file to convert." )
    parser.add_argument( "-o", "--output", help = "The output file. By default this will be the same as the input file.", default = None )
    parser.add_argument( "-n", "--names", help = "Add column and row names from `mtx_cols` and `mtx_rows` files of the same name as the input file.", action = "store_true" )
    parser.add_argument( "-r", "--use_R", type = bool, help = "Use R to convert the mtx file to tsv. (default True) ", default = True )
    
    return parser

def main():
    """
    The main function
    """
    parser = setup_cli()
    args = parser.parse_args()
    
    if args.use_R:
        runR( args )
    else:
        runPy(args)

def runPy(args):
    """
    Runs the script in python
    """
    logger.info( "Reading mtx file..." )
    data = read( args.file )
    
    if args.names:
        logger.info( "Adding column and row names..." )
        data = add_names( data, args.file )

    logger.info( "Writing to tsv file..." )
    outfile = args.file.replace(".mtx", ".tsv") if args.output is None else args.output
    write( data, outfile )
    logger.info( "Done!" )
    
def runR( args ):
    """
    Runs R to convert the mtx file to tsv.
    """
    names = "-n" if args.names else ""
    output = args.output if args.output else args.file.replace( ".mtx", ".tsv" )

    path = os.path.dirname( os.path.abspath( __file__ ) )
    cmd = f"""Rscript {path}/mtx_to_tsv.R -o "{output}" {names} "{args.file}" """
    subprocess.run( cmd, shell = True )

if __name__ == "__main__":
   main()