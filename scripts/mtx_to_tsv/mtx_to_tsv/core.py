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