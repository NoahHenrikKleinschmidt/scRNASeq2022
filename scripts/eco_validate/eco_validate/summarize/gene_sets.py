"""
Summarize gene sets for each cell type acrross separate EcoTyper runs.
"""

import os
import pandas as pd
import eco_validate.core as core


def main( directories : list, outdir : str, config : str = None, **kwargs ):
    """
    Main function for the summarize cell gene sets per-cell type.
    """
    collection = core.CellStateCollection( directories )