"""
This class handles cell type sub-datasets from EcoTyper.
"""

import os

class CellTypeCollection:
    """
    This class assembles the cell types from multiple EcoTyper results directories.

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to get Cell Types from.
    """
    def __init__(self, directories : list ):
        self.cell_types = {}
        self.directories = directories
        
        for directory in self.directories:
            self._find_cell_types( directory )

    def _find_cell_types( self, directory : str ):
        """
        Find the cell types from a single EcoTyper results directory.

        Parameters
        ----------
        directory : str
            The EcoTyper results directory to get cell types from.
        """
        cell_types = [ i for i in os.listdir( directory ) if os.path.isdir( os.path.join( directory, i ) ) ]
        
        if "Ecotypes" in cell_types: 
            cell_types.remove( "Ecotypes" )

        for cell_type in cell_types:
            if cell_type not in self.cell_types:
                self.cell_types[cell_type] = [ os.path.join( directory, cell_type ) ]
            else:
                self.cell_types[cell_type] += [ os.path.join( directory, cell_type ) ]

    def __iter__( self ):
        """
        Iterate over the cell types.
        """
        return iter( self.cell_types )
    
    def __getitem__( self, key ):
        """
        Get the cell type directories.
        """
        return self.cell_types[key]
    