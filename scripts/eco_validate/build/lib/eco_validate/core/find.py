"""
Find data files within the EcoTyper output directories or the EcoTyper internal directories.
"""

import os
import glob

def find_subdirs( parent : str, pattern : str  ):
    """
    Find subdirectories within a directory using glob.
    
    Parameters
    ----------
    parent : str
        The path to the parent directory.
    pattern : str
        The pattern to use for finding subdirectories.
        
    Returns
    -------
    subdirs : list or None
        The subdirectories within the directory.
    """
    subdirs = glob.glob( os.path.join( parent, pattern ) )
    if len( subdirs ) == 0:
        return None
    return subdirs

def find_files( parent : str, pattern : str ):
    """
    Find files within a directory using glob.
    
    Parameters
    ----------
    parent : str
        The path to the parent directory.
    pattern : str
        The pattern to use for finding files.

    Returns
    -------
    files : list or None
        The files within the directory.
    """
    files = glob.glob( os.path.join( parent, pattern ) )
    if len( files ) == 0: 
        return None
    return files
