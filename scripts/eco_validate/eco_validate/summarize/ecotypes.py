"""
Summarize the Ecotype assignments from multiple Ecotyper runs.
Because the state assignment labels and ecotypes are arbitrary due to the 
independet clustering, we shall check the cell-type composition and marker genes
overlap between all ecotypes and establish the similarity between ecotypes.
"""

import os
import eco_validate.core.cell_states as cell_states

class EcoTypeCollection( cell_states.CellStateCollection ):
    """
    This class handles the Ecotype assignments between runs.

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to get ecotypes from.
    """
    def __init__( self, directories : list ):
        super().__init__( directories )
        self.state_assignments = {}

        for cell_type, dirs in self.cell_types.items() :
            self._find_state_assignments( cell_type, dirs ) 
    
    def save( self, directory : str ):
        """
        Save the state assignments of each cell type to a directory (one file per cell type).
        
        Parameters
        ----------
        directory : str
            The directory to save the state assignments to.
        """
        for cell_type, df in self.state_assignments.items():
            df.to_csv( os.path.join( directory, cell_type + "_state_assignment.txt"), sep = "\t" )

    def _find_state_assignments( self, cell_type : str, dirs : list ):
        """
        Find the state assignments from a single cell type from multiple EcoTyper results directories.
        
        Parameters
        ----------
        cell_type : str
            The cell type to find state assignments for.
        dirs : list
            The EcoTyper results directories to get state assignments from.
        """
        state_assignments = pd.DataFrame()

        for dir in dirs:
            

            name = core.find_files( dir, "state_assignment.txt" )
            if not name:
                logging.warning( f"No state assignment file found in {dir}" )
                continue
            
            df = pd.read_csv( name[0], sep = "\t", index_col = 1 )

            name = os.path.basename( os.path.dirname( dir ) )
            state_assignments[ name ] = df[ "State" ]
       
        self.state_assignments[ cell_type ] = state_assignments
    
    def __iter__( self ):
        """
        Iterate over the cell type state_assignments.
        """
        return iter( self.state_assignments )

    def __getitem__( self, key ):
        """
        Get the cell type state_assignments.
        """
        return self.state_assignments[key]

    def __len__( self ):
        """
        Get the number of cell types.
        """
        return len( self.state_assignments )