"""
Defines core functions for converting raw counts to TPM.
"""

import subprocess
from tkinter import E
import pandas as pd
import numpy as np
import re
from alive_progress import alive_bar
import logging

# make a logger
logger = logging.getLogger( name = "tpm_handler" )
logger.setLevel( logging.INFO )
logger.addHandler( logging.StreamHandler() )

def call_gtftools( filename : str, output : str,  mode : str = "l" ):
    """
    Calls gtftools from CLI to perform a computation. 
    By default to calculate lengths.¨

    Parameters
    ----------
    filename : str
        The input GTF file.
    output : str
        The output file.
    mode : str, optional
        The mode of the computation. The default is "l".
        Any valid gtftools mode is allowed.
    """
    cmd = f"gtftools -{mode} {output} {filename}"
    subprocess.call( cmd, shell = True )


def add_gtf_gene_names( filename : str, outfile : str ):
    """
    Adds the gene names to the GTF file.

    Parameters
    ----------
    filename : str
        The input GTF file.
    outfile : str
        The output file.
    """
    orig = pd.read_csv( filename, sep = "\t", header = None, comment = "#", names = ["chr", "source", "type", "start", "end", "score", "strand", "phase", "attributes"] )
    dest = pd.read_csv( outfile, sep = "\t", header = None )

    # now extract the gene names using regex and add as a data column...
    pattern = re.compile( 'gene_name "([A-Za-z0-9-.]+)"' )
    orig["gene_name"] = _match_regex_pattern( pattern, orig )
    
    # and do the same for the gene_ids
    pattern = re.compile( 'gene_id "([A-Za-z0-9-.]+)"' )
    orig["gene_id"] = _match_regex_pattern( pattern, orig )

    # and now merge the two dataframes
    orig = orig[ ["gene_id", "gene_name"] ]
    orig = orig.drop_duplicates()
    dest = dest.merge( orig, left_on = dest.columns[0], right_on = "gene_id" )
    dest = dest.drop( columns = ["gene_id"] )

    # now reorder to place gene_names at second position because normalisation 
    # will by default use the last column so that should be one of the length 
    # columns not the gene_names...
    cols = dest.columns.tolist()
    cols.insert( 1, "gene_name" )
    del cols[-1]
    dest = dest[ cols ]

    dest.to_csv( outfile, sep = "\t", header = False, index = False )
    

def _match_regex_pattern( pattern : str, df : pd.DataFrame ):
    """
    Matches a regex pattern to a dataframe using it's "attributes" column.

    Parameters
    ----------
    pattern : str
        The regex pattern.
    df : pd.DataFrame
        The dataframe.

    Returns
    -------
    list
        The matched values.
    """
    matches = map( lambda x : re.search( pattern, x ), df["attributes"] )
    matches = [ i.group(1) if i is not None else i for i in matches ]
    return matches 

def array_to_tpm( array : np.ndarray, lengths : np.ndarray ):
    """
    Convert raw counts to TPM.

    Parameters
    ----------
    array : np.ndarray
        The raw counts. As a 2D ndarray.
    lengths : np.ndarray
        The lengths of the features. As a 1D ndarray.

    Returns
    -------
    np.ndarray
        The TPM values.
    """
    
    # first convert to log-scale
    log_length = np.log( lengths )
    tpm = np.log( array )

    # now iterate over each column and convert to TPM
    # and store the converted data
    iterations = np.arange( tpm.shape[1] )
    factor = np.log(10**6) 
    with alive_bar( tpm.shape[1], title = "Converting to TPM" ) as bar:
        for i in iterations:
            col = tpm[:,i]
            col = col - log_length

            colsum = np.exp( col )
            colsum = np.sum( colsum ) 
            colsum = np.log( colsum )

            tpm[:,i] = np.exp( col - colsum + factor )
            bar()


    # alternative without a for-loop:
    # NOTE: Has some dimensionality broadcasting issues!!!
    #       Would need fixing...
    # # make the lengths array of the same shape as the raw counts.
    # if len(lengths) != len(array):
    #     raise IndexError( "The length of the lengths array does not match the length of the raw counts array." )
    # lengths = np.column_stack( [lengths] * array.shape[1] )
    
    # # subtract the lengths from the raw counts.
    # tpm = tpm - lengths

    # # now get the column-sums of the counts
    # colsums = np.exp( tpm )
    # colsums = np.sum( colsums, axis = 1 ) 
    # colsums = np.log( colsums )

    # #and adjust the shape again to match
    # colsums = np.row_stack( [colsums] * tpm.shape[1] )
    # colsums = colsums.transpose()

    # # and now normalise by the column sums and adjust per-million
    # factor = np.log( 1e6 ) 
    # tpm = np.exp( tpm - colsums + factor )
    
    return tpm


class Table(object):
    """
    A class for handling a table of counts, and converting raw counts to TPM.

    Parameters
    ----------
    filename : str
        The input count table in TSV format.
    """
    def __init__( self, filename : str, **kwargs ):
        self._src = filename
        self._df = self.read( filename, **kwargs )
        self._lengths = None
        self._raw_counts = None

    def normalise( self, digits : int = 0 ):
        """
        Normalise the raw counts to TPM.

        Parameters
        ----------
        digits : int, optional
            The number of digits to round to. The default is 0.
        """
        if not self._has_lengths:
            raise ValueError( "The table does not have lengths." )

        # store the raw counts
        self._raw_counts = self._df.copy()
        
        # convert to TPM
        tpm = array_to_tpm( self.counts, self.lengths )

        # now round to the given number of digits
        logger.info( "Rounding values..." )
        tpm = np.round( tpm, decimals = digits )
        if digits == 0:
            tpm = np.array( tpm, dtype = np.int64 )

        # and now replace the raw counts in all 
        # columns that contain counts (i.e. all but the first)
        self._df[ self._count_columns( self._df ) ] = tpm

        return self

    def set_lengths( self, filename : str, which : str = None, id_col : str = None, name_col : str = None ):
        """
        Sets the lengths of the features.

        Parameters
        ----------
        filename : str
            The file containing the lengths of the features.
        which : str, optional
            The column name of the lengths. The default is None (in which case the last column is used).
        id_col : str, optional
            The column name of the IDs. The default is None (in which case the first column is used).
        name_col : str, optional
            The column name of the names. The default is None (in which case the second column is used).
        """
        lengths = self.read( filename )

        # get only the relevant subset of lengths for the actually present features
        if id_col is None:
            id_col = lengths.columns[0]

        if name_col is None:
            name_col = lengths.columns[1]

        # get all the currently held ids in the countTable
        ref_ids = self.ids
        mask = lengths[ id_col ].isin( ref_ids )
        lengths = lengths[ mask ]

        # and now sort to ensure the same order is preserved
        lengths = lengths.set_index( id_col )
        lengths = lengths.reindex( index = ref_ids )
        lengths = lengths.reset_index()

        # now only get a single length column from the lengths dataframe
        if which is None:
            which = lengths.columns[-1]
        elif which not in lengths.columns:
            raise ValueError( f"The column name '{which}' is not in the file {filename}" )
        self._lengths = lengths[ [id_col, name_col, which] ]
        return self
    
    def get_lengths( self ): 
        """
        Returns the lengths of the features.

        Returns
        -------
        lengths : pandas.Series or None
            The lengths of the features.
        """
        return self._lengths

    def get(self):
        """
        Returns the table.

        Returns
        -------
        df : pandas.DataFrame
            The table.
        """
        return self._df

    def read( self, filename : str, sep : str = "\t", **kwargs ): 
        """
        Reads a table from a file.

        Parameters
        ----------
        filename : str
            The input file.
        sep : str, optional
            The separator of the table. The default is "\t".

        Returns
        -------
        df : pandas.DataFrame
            The table.
        """
        df = pd.read_csv( 
                            filename, 
                            sep = sep, 
                            comment = "#", 
                            **kwargs
                        ) 
        return df

    def save( self, filename : str, use_names : bool = False ): 
        """
        Saves the table to a file.

        Parameters
        ----------
        filename : str
            The output file.
        use_names : bool
            Save the file with gene_names instead of gene_ids in the first column.
        """
        logger.info( "Saving to file..." )
        if use_names:
            self._df[ self._df.columns[0] ] = self.names
        self._df.to_csv( filename, sep = "\t", index = False, engine = "c" )
        logger.info( f"Saved to file: {filename}" )
        return self

    @property
    def raw_counts( self ):
        """
        Returns the raw counts.

        Returns
        -------
        counts : numpy.ndarray
            The raw counts.
        """
        if self._raw_counts is None:
            return self.counts
        return self._raw_counts[ self._count_columns( self._raw_counts ) ].to_numpy()
    
    @property
    def counts( self ):
        """
        Returns the raw or TPM counts (if normalisation was performed).

        Returns
        -------
        counts : numpy.ndarray
            The raw or TPM counts.
        """
        return self._df[ self._count_columns( self._df ) ].to_numpy()

    @property
    def lengths( self ):
        """
        Returns the lengths of the features.

        Returns
        -------
        lengths : numpy.ndarray or None
            The lengths of the features.
        """
        return self._lengths[ self._lengths.columns[-1] ].to_numpy()

    @property
    def ids(self):
        """
        Returns the IDs of the features.

        Returns
        -------
        ids : list
            The IDs of the features.
        """
        return list( self._df[ self._df.columns[0] ] ) 

    @property
    def names(self):
        """
        Returns the names of the features.

        Returns
        -------
        names : list
            The names of the features.
        """
        return list( self._lengths[ self._lengths.columns[1] ] )

    @property
    def _has_lengths(self): 
        """
        Checks if the table has lengths.

        Returns
        -------
        has_lengths : bool
            True if the table has lengths.
        """
        return self._lengths is not None

    @staticmethod
    def _count_columns( df ):
        """
        Returns the names of the columns that contain counts.

        Returns
        -------
        count_columns : list
            The names of the columns that contain counts.
        """
        return df.columns[1:]

    def __repr__(self) -> str:
        return f"Table(file='{self._src}')"