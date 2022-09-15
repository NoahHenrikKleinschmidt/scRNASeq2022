"""
Classes to handle gene sets.
"""

import os
import pandas as pd
import eco_validate.core.settings as settings

class GeneSetCollection:
    """
    This class handles a collection of gene sets for different cell types.
    
    Parameters
    ----------
    gene_sets : dict
        A dictionary with cell type labels as keys and a dataframe of extracted genes with a "State" column to describe their assigned state.
    """
    def __init__( self, gene_sets : dict = None ):
        self._gene_sets = gene_sets if gene_sets else {}

    def keys( self ):
        return self._gene_sets.keys()
    
    def values( self ):
        return self._gene_sets.values()

    def items( self ):
        return self._gene_sets.items()

    def save( self, file_or_directory : str ):
        """
        Save the gene sets either to a single condensed file or as separate files (one per cell type) into a directory.

        Parameters
        ----------
        file_or_directory : str
            The file or directory to save the gene sets to.
        """
        if os.path.isdir( file_or_directory ):
            for cell_type, df in self._gene_sets.items():
                df.to_csv( os.path.join( file_or_directory, cell_type + settings.gene_sets_suffix ), sep = "\t" )
        else:
            total_df = list( self._gene_sets.values() )

            for cell_type, i in zip( self._gene_sets.keys(), total_df ): 
                i[ settings.cell_type_col ] = cell_type

            total_df = pd.concat( total_df )
            total_df.to_csv( file_or_directory, sep = "\t" )

    def subsets( self, cell_type : str = None ):
        """
        Return a groupby object for the given cell_type dataframe. 
        
        Parameters
        ----------
        cell_type : str
            The cell type label. If none is provided a generator is returned with a groupby object for each cell type.
        
        Returns
        -------
        groupby
            A groupby object for the given cell_type dataframe. Or a generator with a groupby object for each cell type.
        """
        if cell_type:
            return self._gene_sets[ cell_type ].groupby( settings.state_col )
        else:
            return ( i.groupby( settings.state_col ) for i in self._gene_sets.values() )

    @property
    def cell_types( self ):
        return self._gene_sets.keys()

    def __setitem__( self, key, value ):
        if not isinstance( value, pd.DataFrame ):
            raise ValueError( "Gene sets must be pandas dataframes." )
        elif settings.state_col not in value.columns:
            raise ValueError( f"Gene sets must have a '{settings.state_col}' column." )
        self._gene_sets[key] = value

    def __getitem__( self, key ):
        if isinstance( key, tuple ):
            key, state = key
            
        df = self._gene_sets[key]
        if state:
            df = df[  df[ settings.state_col ] == state  ]
        return df

    def __iter__( self ):
        return iter( self._gene_sets )
    
    def __len__( self ):
        return len( self._gene_sets )
    
    def __contains__( self, key ):
        return key in self._gene_sets
    
    def __repr__( self ):
        return f"GeneSetCollection({ list( self._gene_sets.keys() ) })"


class GeneSetOverlap:
    """
    A class to handle the overlap between different cell states and separate Ecotyper runs for a single cell type.

    Parameters
    ----------
    cell_type : str 
        The cell type label.
    
    state_assignments : dict
        A pandas dataframe with a genes as index, a "State" column specifying the state to which the gene was assigned, and a "run" column specifying which Ecotyper run the assignment is from.
    """
    def __init__( self, cell_type : str, state_assignments : pd.DataFrame ):
        self.cell_type = cell_type
        self.state_assignments = state_assignments

    def compute_overlap( self, percent : bool = False ):
        """
        Compute the overlap between between separate Ecotyper runs for each cell state individually.

        Parameters
        ----------
        percent : bool
            If True, compute the overlap as a percentage of the total set of genes per state.
        """
        final = []
        total = set( self.state_assignments.index )
        for run, subset in self.state_assignments.groupby( settings.ecotyper_experiment_col ):
            
            overlap = BaseOverlap( total, set( subset.index ) )
            subset = overlap.get( percent = percent )
            subset.index = [run]

            final += [subset]

        final = pd.concat( final, axis = 0 )
        final.insert( 0, settings.cell_type_col, self.cell_type )
        return final

class BaseOverlap:
    """
    This class handles a single overlap between two sets of genes.

    Parameters
    ----------
    a : set
        The first set of genes.
    b : set
        The second set of genes.
    """
    def __init__( self, a : set, b : set ):
        self.a = a
        self.b = b
        self.overlap = a.intersection( b )
        self.total = len( a.union( b ) )
        self.overlap_percent = len( self.overlap ) / self.total

    def get( self, percent : bool = False ):
        """
        Get a pandas dataframe of the overlaps between the two sets, either in percentages
        or in absolute counts (in which case a "total" column is added).

        Parameters
        ----------
        percent : bool
            If True, return the overlap in percentages.
        """
        if percent:
            return pd.DataFrame( { "overlap" : [self.overlap_percent] }  )
        else:
            return pd.DataFrame( { "overlap" : [len(self)], "total" : [self.total] } )

    def __len__( self ):
        return len( self.overlap )
