"""
Using the `summarize` command, this module allows to combine the results of ecotyper results into a single file and summary figure.
This is currently implemented for:
    - rank_data
"""

from .ranks import find_rank_datafiles, combine_ranks
from .ranks import heatmap as rank_heatmap

from .cell_states import CellStateCollection
from .cell_states import scatterplot as cell_state_scatterplot
from .cell_states import heatmap as cell_state_heatmap