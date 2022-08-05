# Defines the core functions for mtx_to_tsv

from scipy.io import mmread
import pandas as pd

    
formatters = { 
                "-" : "_", 
                " " : "." 
            } 
"""
A dictionary containing special characters that must be replaced by something 
else in order to be able to use the names of the genes in the tsv file.
"""

def read( filename: str ):
    """
    Reads a mtx file and returns a pandas dataframe.

    Parameters
    ----------
    filename : str
        The name of the mtx file to read.

    Returns
    -------
    pandas.DataFrame
        The dataframe containing the mtx file.
    """
    return pd.DataFrame( mmread( filename ).toarray() )



def add_names( data : pd.DataFrame, filename : str ):
    """
    Adds column and row names to a dataframe.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataframe to add names to.
    filename : str
        The name of the mtx file.

    Returns
    -------
    pandas.DataFrame
        The dataframe with names.
    """
    cols = pd.read_csv( 
                            filename.replace( ".mtx", ".mtx_cols" ), 
                            sep = "\t", header = None, names = ["name"] 
                        )
    rows = pd.read_csv( 
                        filename.replace( ".mtx", ".mtx_rows" ), 
                        sep = "\t", header = None, names = ["orig", "name"] 
                    )
    
    # now ensure that the names are in the proper format so EcoTyper won't cry around...
    for old, new in formatters.items():
        cols.name = cols.name.str.replace( old, new )
        rows.name = rows.name.str.replace( old, new )

    data.columns = cols.name
    data.index = rows.name

    return data

def write( data : pd.DataFrame, filename : str ):
    """
    Writes a dataframe to a tsv file.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataframe to write.
    filename : str
        The name of the tsv file.
    """
    data.to_csv( filename, sep = "\t" )