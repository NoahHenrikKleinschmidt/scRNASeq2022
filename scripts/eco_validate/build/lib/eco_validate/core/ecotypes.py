"""
This class handles EcoType assignments between different EcoTyper runs.
"""

import logging
import eco_validate.core.find as find
import eco_validate.core.cell_states as cell_states

class EcoTypeCollection( cell_states.CellStateCollection ):
    """
    This class handles EcoType assignments between separate EcoTyper runs.

    Parameters
    ----------
    directories : list
        List of EcoTyper results (output) directories to get ecotypes from.
    """
    def __init__( self, directories : list ):
        super().__init__( directories )
        self.ecotype_assignments = {}

        for cell_type, dirs in self.cell_types.items() :
            self._find_state_assignments( cell_type, dirs )