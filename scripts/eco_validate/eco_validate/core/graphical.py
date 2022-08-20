"""
Core graphical auxiliary functions
"""

import numpy as np

def make_layout_from_list( ref_list ):
    """
    Generates a subplot layout based on a list instead of dataframe column.
    
    Note
    ----
    This is a one-to-one copy of the `make_layout_from_list` function I 
    wrote for the `qpcr` package in `qpcr._auxiliary.graphical`. 

    Parameters
    ----------
    ref_list : list
        The list of entries to be included in the layout.
    
    Returns
    -------
    layout : tuple
        The layout of the subplots. As ncols, nrows.
    """
    ref_length = len( set(ref_list) )

    if ref_length == 1: 
        return (1, 1)

    if ref_length % 2 == 0:
        nrows = 2
        if ref_length % 4 == 0 and ref_length > 4:
            nrows = 4
    elif ref_length % 6 == 0:
            nrows = 6
    else: 
        nrows = 3

    ncols = int(np.ceil(ref_length / nrows))
    if ncols * nrows >= ref_length:
        return ncols, nrows
    else:
        ncols = ncols+1
        return ncols, nrows