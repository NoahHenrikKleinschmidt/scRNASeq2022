"""
Combine the ranks assignment for the different cell types from multiple runs.
"""

import logging
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

from eco_validate.core import EcoTyperConfig

def main( directories : list, filename : str = None, config = None, **kwargs ):
    """
    Combine the ranks assignment for the different cell types from multiple runs.
    
    Note
    ----
    This is the CLI main function.

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to search for rank datafiles.
    filename : str
        Filename to save the assembled data and heatmap to. 
        If none is given, no assembled data is saved and the heatmap will be shown instead.
    config : EcoTyperConfig
        EcoTyper configuration object used for the EcoTyper runs. 
        If provided this will add the Cophentic cutoff used in rank selection to the heatmap title.
    **kwargs 
        are passed to the heatmap function.
    """
    # Find the rank datafiles from multiple runs.
    rank_datafiles = find_rank_datafiles( directories )

    # Combine the ranks assignment for the different cell types from multiple runs.
    combined_ranks = combine_ranks( rank_datafiles )
    if filename: 
        combined_ranks.to_csv( filename, sep = "\t" )

        # and adjust for the heatmap function
        filename = f"{ filename }.heatmap.png"

    # Plot a heatmap of the combined ranks.
    if config:
        config = EcoTyperConfig( config )
        title = kwargs.get( "title", "Combined ranks" )
        kwargs["title"] = f"{ title } (Cophentic cutoff: { config.cophentic_cutoff })"
    heatmap( combined_ranks, filename, **kwargs )
    
    logging.info( "Combined ranks saved to: " + filename )


def find_rank_datafiles( directories : list ):
    """
    Find the rank datafiles from multiple runs in multiple directories.

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to search for rank datafiles.
    """
    # Find the rank datafiles from multiple runs.
    rank_datafiles = []
    for directory in directories:
        rank = os.path.join( directory, "rank_data.txt" )
        if os.path.isfile( rank ):
            rank_datafiles += [rank]
        else:
            logging.warning( f"directory '{ directory }' does not have a rank_data.txt file." )
    return rank_datafiles


def combine_ranks( rank_datafiles : list ):
    """
    Combine the ranks assignment for the different cell types from multiple runs.
    
    Parameters
    ----------
    rank_datafiles : list
        List of rank datafiles to combine.

    Returns
    -------
    combined_ranks : pandas.DataFrame
        Combined ranks dataframe with cell types as rows (as index) and ecotyper-ranks as columns (one column per run).
    """
    # Combine the ranks assignment for the different cell types from multiple runs.
    combined_ranks = pd.DataFrame()
    for rank_datafile in rank_datafiles:
        logging.info( f"reading { rank_datafile }" )

        name = os.path.dirname( rank_datafile )

        # Read the rank datafile and make sure use the rank dataset name for the column name.
        ranks = pd.read_csv( rank_datafile, sep="\t", index_col=0, quotechar = '"' )
        combined_ranks[ name ] = ranks["Chosen_Rank"]

    return combined_ranks

def heatmap( combined_ranks : pd.DataFrame, filename : str = None, **kwargs ):
    """
    Plot a heatmap of the combined ranks.
    
    Parameters
    ----------
    combined_ranks : pandas.DataFrame
        Combined ranks dataframe with cell types as rows (as index) and ecotyper-ranks as columns (one column per run).
    filename : str
        Filename to save the heatmap to. If none is given, then the heatmap will be shown instead.
    """
    # remove the full file paths from the column names (files)
    if not kwargs.pop( "fullpath", False ):
        combined_ranks.columns = combined_ranks.columns.str.split("/").str[-1]

    # setup the figure
    figsize = kwargs.pop("figsize", (10,10) )
    dpi = kwargs.pop( "dpi", 300 )
    fig, ax = plt.subplots( figsize = figsize, dpi = dpi )

    title = kwargs.pop( "title", "Combined ranks" )
    ax.set( title = title )
    
    # adjust the colorbar on the side of the figure
    cbar_kws = kwargs.pop( "cbar_kws", {} )
    cbar_kws["shrink"] = cbar_kws.get("shrink", 0.25)
    cbar_kws["anchor"] = cbar_kws.get("anchor", (0,0))
    cbar_kws["aspect"] = cbar_kws.get("aspect", 10)
    kwargs["cbar_kws"] = cbar_kws

    # and make sure to use viridis as color map 
    kwargs["cmap"] = kwargs.get("cmap", "viridis")

    sns.heatmap( combined_ranks, annot = True, fmt = "d", ax = ax, **kwargs )
    
    plt.tight_layout()

    if not filename: 
        plt.show()
    else:
        plt.savefig( filename )
        plt.close()

