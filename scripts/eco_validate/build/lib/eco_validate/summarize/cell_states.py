"""
Summarize the cell state assignments accross runs.
"""

import logging
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import eco_validate.core as core
import eco_validate.core.graphical as graphical 

from alive_progress import alive_bar

def main( directories : list, outdir : str, config : str = None, **kwargs ):
    """
    Main function for the summarize cell state assignments per-cell type.

    Parameters
    ----------
    directories : list
        List of directories to summarize the cell state assignments from.
    outdir : str
        Directory to store assignments summaries to. One assignment file per cell type and an overall summary figure file.
    config : str
        The EcoTyper configuration yml file used to compute the summarized results. (optional)
    """
    if config:
        config = core.EcoTyperConfig( config )
        suptitle = config.dataset
    else:
        suptitle = None

    kwargs["suptitle"] = kwargs.pop("suptitle", suptitle )

    data = core.CellStateCollection( directories )

    scatterfile = None
    heatmapfile = None
    if outdir: 
        data.save( outdir )
        scatterfile = f"{outdir}/cell_states.scatterplot.png"
        heatmapfile = f"{outdir}/cell_states.heatmap.png"

    scatterplot( data, filename = scatterfile, **kwargs )
    heatmap( data, filename = heatmapfile, **kwargs )
    
    if outdir:
        print( f"Saving outputs to {outdir}" )

def scatterplot( data : (core.CellStateCollection or pd.DataFrame), show_sample_labels : bool = False, filename: str = None, **kwargs ):
    """
    Create a scatterplot of the state assignments per sample and run.
    
    Parameters
    ----------
    data : CellStateCollection or pd.DataFrame
        Either the collection of state assignments to plot (will generate subplots for each cell type), or a specific dataframe to plot.
    show_sample_labels : bool
        Whether to show the sample labels on the scatterplot. Since the samples may be a long list, by default this is disabled to avoid crowding the figure.
    filename : str
        The filename to save the figure to. If not specified, the figure will not be saved.
    **kwargs : dict
        Keyword arguments to pass to seaborn.scatterplot.
    """
    if isinstance( data, pd.DataFrame ):

        ax = kwargs.pop( "ax", None )
        if ax is None:
            fig, ax = plt.subplots( figsize = kwargs.pop( "figsize", (10,10) ), 
                                    dpi = kwargs.pop( "dpi", 300 ) )

            fig.suptitle( kwargs.pop( "suptitle", None ) )

        ax.set( title = kwargs.pop( "title", "State Assignments" ),
                xlabel = kwargs.pop( "xlabel", "Sample" ),
                ylabel = kwargs.pop( "ylabel", "State" ) )

        alpha = kwargs.pop( "alpha", 0.5 )

        # now iterate over each column in the dataframe and plot their state assignments
        
        for col in data.columns:
            
            try:

                # in case we have a NaN in there we convert that to string
                _col = data[col].astype(str).astype("category")

                ax.scatter( x = data.index.astype("category"), 
                            y = _col, 
                            label = col,
                            alpha = alpha,
                            linewidth = 0,
                            **kwargs )

            except Exception as e:
                logging.warning( f"Could not plot {col} : {e}" )
                continue

        if not show_sample_labels:
            ax.set( xticklabels = [], xticks = [] )


        ax.legend( bbox_to_anchor = (1.05, 1), frameon = False )
        plt.tight_layout()

        if filename:
            plt.savefig( filename )
            plt.close()

    elif isinstance( data, core.CellStateCollection ):
        
        ncols, nrows = graphical.make_layout_from_list( data.cell_types.keys() )
        fig, axs = plt.subplots( nrows, ncols, figsize = kwargs.pop("figsize", (10,10)), dpi = kwargs.pop("dpi", 300) )
        fig.suptitle( kwargs.pop("suptitle", None) )
        
        with alive_bar( len(data), title = "Generating scatterplot" ) as bar:
            for cell_type, ax in zip( data.state_assignments, axs.reshape(axs.size) ):
                scatterplot( data[cell_type], show_sample_labels, ax = ax, title = cell_type, **kwargs )
                bar()

        if filename: 
            plt.savefig( filename )
            plt.close()

def heatmap( data : (core.CellStateCollection or pd.DataFrame), show_sample_labels : bool = False, filename : str = None, **kwargs ):
    """
    Create a heatmap summary of the cell state assignments per run and celltype.
    """
    if isinstance( data, pd.DataFrame):

        ax = kwargs.pop( "ax", None )
        if ax is None:
            fig, ax = plt.subplots( figsize = kwargs.pop( "figsize", (10,10) ), 
                                    dpi = kwargs.pop( "dpi", 300 ) )

            fig.suptitle( kwargs.pop( "suptitle", None ) )
        
        title = kwargs.pop( "title", "State Assignments" )
        cmap = kwargs.pop( "cmap", "viridis" )

        # adjust the colorbar on the side of the figure
        cbar_kws = kwargs.pop( "cbar_kws", {} )
        cbar_kws["shrink"] = cbar_kws.get("shrink", 0.25)
        cbar_kws["anchor"] = cbar_kws.get("anchor", (0,0))
        cbar_kws["aspect"] = cbar_kws.get("aspect", 10)
        kwargs["cbar_kws"] = cbar_kws

        # a function to extract the numbers from the S01 state labels for heatmap plotting...
        for i in data: data[i] = data[i].astype(str).apply( _to_numbers )

        sns.heatmap( data.transpose(), cmap = cmap, ax = ax, **kwargs )

        ax.set( title = title,
                xlabel = kwargs.pop( "xlabel", "Sample" ),
                ylabel = kwargs.pop( "ylabel", "State" ) )
        
        ax.grid( axis = "y", which = "minor" )

        if not show_sample_labels: 
            ax.set( xticklabels = [], xticks = [] )

        plt.tight_layout()

        if filename: 
            plt.savefig( filename )
            plt.close()
    
    elif isinstance( data, core.CellStateCollection ):

        ncols, nrows = graphical.make_layout_from_list( data.cell_types.keys() )
        fig, axs = plt.subplots( nrows, ncols, figsize = kwargs.pop("figsize", (10,10)), dpi = kwargs.pop("dpi", 300) )
        fig.suptitle( kwargs.pop("suptitle", None) )
        
        with alive_bar( len(data), title = "Generating heatmap" ) as bar:
            for cell_type, ax in zip( data.state_assignments, axs.reshape(axs.size) ):
                
                try:
                    heatmap( data[cell_type], show_sample_labels, ax = ax, title = cell_type, **kwargs )
                    bar()
                except Exception as e:
                    logging.warning( f"Could not plot {cell_type} : {e}" )
                    continue

        if filename: 
            plt.savefig( filename )
            plt.close()

def _to_numbers( x ):
    """
    A function to extract numbers from strings as S01, S02, S03, etc. -> 1,2,3, etc.
    """
    last = x[-1]
    if last.isdigit():
        return int(last)
    else:
        return np.nan
