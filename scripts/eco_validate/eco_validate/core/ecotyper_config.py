"""
Read an EcoTyper config yaml file.
"""

import os
import yaml
from yaml.loader import SafeLoader

def read_ecotyper_config( filename : str ):
    """
    Reads the config file for an EcoTyper experiment.

    Parameters
    ----------
    filename : str
        The path to the config file.
    
    Returns
    -------
    config : dict
        The config file as a dictionary.
    """
    if not os.path.exists( filename ):
        raise FileNotFoundError( f"{filename} does not exist." )
    with open( filename, 'r' ) as f:
        config = yaml.load( f, SafeLoader )
    return config


class EcoTyperConfig:
    """
    This class handles the EcoTyper configuration yaml data.

    Parameters
    ----------
    filename : str
        The path to the config file.
    """
    def __init__( self, filename : str ):
        self.config = read_ecotyper_config( filename )
    
    @property
    def dataset( self ):
        """
        The dataset name used
        """
        return self.config["default"]["Input"]["Discovery dataset name"]

    @property
    def expression_matrix( self ):
        """
        The expression matrix used
        """
        return self.config["default"]["Input"]["Expression matrix"]
    
    @property
    def annotation_file( self ):
        """
        The annotation file used
        """
        return self.config["default"]["Input"]["Annotation file"]
    
    @property
    def annotation_columns( self ):
        """
        The annotation columns used for plotting the heatmaps
        """
        return self.config["default"]["Input"]["Annotation file column(s) to plot"]
    
    @property
    def output_dir( self ):
        """
        The output directory used
        """
        return self.config["default"]["Output"]["Output folder"]
    
    @property
    def cophentic_cutoff( self ):
        """
        The cophentic cutoff used
        """
        return self.config["default"]["Pipeline settings"]["Cophenetic coefficient cutoff"]