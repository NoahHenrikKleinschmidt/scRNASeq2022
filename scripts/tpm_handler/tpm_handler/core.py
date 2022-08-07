"""
Defines core functions for converting raw counts to TPM.
"""

import subprocess
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


def add_gtf_gene_names( filename : str, outfile : str, swap_ids_and_names : bool = False ):
    """
    Adds the gene names to the GTF file.

    Parameters
    ----------
    filename : str
        The input GTF file.
    outfile : str
        The output file.
    swap_ids_and_names : bool, optional
        Whether to swap the IDs and names. The default is False.
        If True then the Ids (1st column) and names (2nd column by default)
        will be swapped so that names are the 1st column and IDs are the 2nd column.
    """
    orig = pd.read_csv( filename, sep = "\t", header = None, comment = "#", names = ["chr", "source", "type", "start", "end", "score", "strand", "phase", "attributes"] )
    dest = pd.read_csv( outfile, sep = "\t" )

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
    idx = 0 if swap_ids_and_names else 1
    cols.insert( idx, "gene_name" )
    del cols[-1]
    dest = dest[ cols ]

    dest.to_csv( outfile, sep = "\t", index = False )
    

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
    factor = np.log(10**6) 
    iterations = np.arange( tpm.shape[1] )
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
    
    logger.debug( f"At the end of array_to_tpm {tpm.shape=}" )
    return tpm

def round_tpm( tpm : np.ndarray, digits : int = 5 ):
    """
    Rounds the TPM values to a certain number of digits.

    Parameters
    ----------
    tpm : np.ndarray
        The TPM values.
    digits : int, optional
        The number of digits to round to. The default is 5.

    Returns
    -------
    np.ndarray
        The rounded TPM values.
    """
    iterations = np.arange( tpm.shape[1] )
    with alive_bar( tpm.shape[1], title = f"Rounding to {digits} digits" ) as bar:
        for i in iterations:
            col = tpm[:,i]
            col = np.round( col, digits )
            tpm[:,i] = col
            bar()
    logger.debug( f"At the end of round_tpm {tpm.shape=}" )
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
        kwargs[ "index_col" ] = kwargs.get( "index_col", 0 )
        self._counts = self.read( filename, **kwargs )
        self.tpm = None
        self._lengths = None
        self._raw_counts = None
        self._full_counts = None
        self._memorize = False

    def memorize( self ):
        """
        Store the original (pre-filtered) and raw (unnormalised) counts.
        """
        self._memorize = True

    def normalise( self, digits : int = 5 ):
        """
        Normalise the raw counts to TPM.

        Parameters
        ----------
        digits : int, optional
            The number of digits to round to. The default is 5.
        """
        if not self._has_lengths:
            raise ValueError( "The table does not have lengths." )

        # store the raw counts
        if self._memorize:
            self._raw_counts = self._counts.copy()
        
        # convert to TPM
        self.tpm = array_to_tpm( self.counts, self.lengths )
        
        # now round to the given number of digits
        logger.info( "Rounding values..." )
        self.tpm = self.round( digits )
        
        # and now replace the raw counts in all 
        # columns that contain counts (i.e. all but the first)
        logger.debug( "Current values ")
        logger.debug( str( self._counts.head() ) )
        logger.info( "Replacing raw counts with TPM values..." )
        new_df = pd.DataFrame( 
                                    self.tpm, 
                                    columns = self._counts.columns, 
                                    index = self._counts.index 
                            )

        logger.debug( "New values")
        logger.debug( str( new_df.head() )  ) 
        self._counts = new_df

        return self

    
    def round(self, digits):
        """
        Round tpm values to a given number of digits.

        Parameters
        ----------
        digits : int
            The number of digits to round to.
        """
        return round_tpm( self.tpm, digits )

    def set_lengths( self, filename : str, which : str = None, id_col : str = None, name_col : str = None, **kwargs ):
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
            The column name of the (gene) names. The default is None (in which case the second column is used).
            Note, even if your datafile does not specify gene names a "name column" will still be extracted. 
            However, you can adjust not to include the column later for saving the TPM-converted file.
        """
        
        # store the original data
        if self._memorize:
            self._full_counts = self._counts.copy()

        # get only the relevant subset of lengths for the actually present features
        if id_col is None:
            id_col = 0
        kwargs[ "index_col" ] = kwargs.get( "index_col", id_col )

        lengths = self.read( filename, **kwargs )

        # check if we have a specified name for the index column
        # this will first check for an index name in the counts data
        # and then for a name in the lengths data. It will overwrite the 
        # current index name in both dataframes with the specified name.
        index_name = self._counts.index.name
        if not index_name:
            index_name = lengths.index.name
            if not index_name:
                logger.warning( "No index name could be identified! Will use `gene_id` as index name." )
                index_name = "gene_id"

        # get all the currently held ids in the countTable
        # and mask the data to only those gene to which reference 
        # lengths are available, and therefore TPMs can be calculated.
        logger.debug( "Before masking:", len( lengths ) )

        mask_lengths = lengths.index.isin( self._counts.index )
        mask_counts = self._counts.index.isin( lengths.index )

        lengths = lengths.iloc[ mask_lengths,: ]
        self._counts = self._counts.iloc[ mask_counts,: ]

        logger.debug( "After masking:", len( lengths ) )

        # and now sort to ensure the same order is preserved
        lengths = lengths.reindex( index = self._counts.index )

        lengths.index.name = index_name
        self._counts.index.name = index_name


        # get which names to extract from the lengths dataframe
        if name_col is None:
            name_col = 0 if id_col == 0 else 1            
            name_col = lengths.columns[name_col]

        # now only get a single length column from the lengths dataframe
        if which is None:
            which = lengths.columns[-1]
        elif which not in lengths.columns:
            raise ValueError( f"The column name '{which}' is not in the file {filename}" )
        
        # and finally restrict our length data to only the name and lengths column
        # as well as the index which holds the ids...
        self._lengths = lengths.loc[ :,[name_col, which] ]
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
        return self._counts

    def read( self, filename : str, sep : str = "\t", **kwargs ) -> pd.DataFrame: 
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
        logger.info( f"Reading input file... (this may take a while)" )
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
        logger.info( "Saving to file... (this may take a while)" )
        if use_names:
            self.adopt_name_index()
        self._counts.to_csv( filename, sep = "\t", index = True )
        logger.info( f"Saved to file: {filename}" )
        return self

    def adopt_name_index( self ):
        """
        Adopts the extracted name column of the lengths dataframe as the new 
        dataframe index for both the lengths and counts data.

        Note
        ----
        This will only affect the raw and final counts (in TPM if normalise has been called),
        but it will not affect the original counts!
        """
        index = self._lengths.iloc[:,0]
        self._counts.index = index
        self._lengths.index = index
        self._raw_counts.index = index


    @property
    def raw_data( self ):
        """
        Returns the originally provided counts data.

        Note    
        -----
        This contains all the provided genes and their counts,
        including those for which no lengths are available.

        Returns
        -------
        raw_data : pandas.DataFrame
            The originally provided counts data.
        """
        return self._full_counts

    @property
    def raw_counts( self ):
        """
        Returns the raw counts.

        Note
        ----
        These are cropped to only genes that were found to have a 
        corresponding length in the lengths file and for which therefore
        TPM conversion could be performed. If you wish to access the original
        (pre filtered) data, use the raw_data attribute instead.

        Returns
        -------
        counts : np.ndarray
            The raw counts.
        """
        if self._raw_counts is None:
            return self.counts
        return self._raw_counts.to_numpy()
    
    @property
    def counts( self ):
        """
        Returns the raw or TPM counts (if normalisation was performed).

        Note
        ----
        These are cropped to only genes that were found to have a 
        corresponding length in the lengths file and for which therefore
        TPM conversion could be performed. If you wish to access the original
        (pre filtered) data, use the raw_data attribute instead.

        Returns
        -------
        counts : np.ndarray
            The raw or TPM counts.
        """
        return self._counts.to_numpy()


    @property
    def ids(self) -> np.ndarray:
        """
        Returns the IDs of the features.

        Returns
        -------
        ids : np.ndarray
            The IDs of the features.
        """
        return self._counts.index.to_numpy()

    @property
    def names(self) -> np.ndarray:
        """
        Returns the names of the features.

        Returns
        -------
        names : np.ndarray
            The names of the features.
        """
        return self._lengths.iloc[ :,0 ].to_numpy()

    @property
    def lengths( self ) -> np.ndarray:
        """
        Returns the lengths of the features.

        Returns
        -------
        lengths : numpy.ndarray or None
            The lengths of the features.
        """
        return self._lengths.iloc[ :,-1 ].to_numpy()

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
    
    def __str__(self) -> str:
        return self._counts
    
    def __len__(self) -> int:
        return len(self._counts)
    