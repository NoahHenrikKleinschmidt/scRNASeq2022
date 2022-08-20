"""
This is the command line interface for `summarize`.
"""

import argparse
import eco_validate.summarize.ranks as ranks
import eco_validate.summarize.cell_states as states

def setup( parent ):
    """
    Set up the command line interface for summarize.
    """
    descr = "Summarize the results of multiple EcoTyper runs."
    parser = parent.add_parser( "summarize", description = descr )
    parser.add_argument( "directories", nargs = "+", help = "EcoTyper results (output) directories to summarize together." )
    parser.add_argument( "-o", "--output", help = "Output directory to store the summary in. By default the current working directory.", default = "." )
    parser.add_argument( "-c", "--config", help = "The EcoTyper configuration yml file used to compute the summarized results. (optional)", default = None )

    parser.add_argument( "-r", "--ranks", action = "store_true", help = "Assemble and compare the ranks assignment from ecotyper runs." )
    parser.add_argument( "-s", "--states", action = "store_true", help = "Assemble and compare the cell state assignment from ecotyper runs per cell-type." )
    parser.set_defaults( func = main )

def main( args ):
    """
    Main function for the summarize command line interface.
    """
    if args.ranks:
        outfile = f"{ args.output }/ranks_summary.tsv"
        ranks.main( args.directories, outfile, args.config  )
    if args.states:
        states.main( args.directories, args.output, args.config  )