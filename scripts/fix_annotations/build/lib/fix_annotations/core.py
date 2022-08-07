"""
Defines the core functions to make sure an annotation file is conformant with EcoTypers requirements with regard to the formatting of ID, Sample, and CellType columns.
"""

import os
from re import sub
import pandas as pd

import logging
import glob
from alive_progress import alive_bar
import subprocess

# make a logger
logger = logging.getLogger( name = "fix_annotations" )
logger.setLevel( logging.INFO )
logger.addHandler( logging.StreamHandler() )

default_formats = {
            "-" : ".",
            " " : "_",
        }
"""
A dictionary of invalid characters which must be replaced with a valid character.
As key (invalid) : value (valid) pairs.
"""

def read_formats_file( filename : str ) -> dict:
    """
    Reads a file containing a dictionary of invalid characters to valid characters.
    
    Parameters
    ----------
    filename : str
        The name of the file containing the dictionary.
    
    Returns
    -------
    dict
        A dictionary of invalid characters to valid characters.
    """
    with open( filename, "r" ) as f:
        lines = f.readlines()
    formats = {}
    for line in lines:
        line = line.strip()
        if line.startswith( "#" ) or line == "":
            continue
        key, value = line.split( ":" )
        formats[ key.strip() ] = value.strip()
    return formats

# make classes to imitate the dataframe columns and indices.
# They are just pd.Series but giving them extra names will make the 
# code easier to understand...

class Pseudo( pd.Series ):
    """
    A class to imitate the dataframe columns and indices.
    It is just pd.Series but giving them extra names will make the 
    code easier to understand...
    """
    def __init__( self, data : list, name : str ):
        super().__init__( data, name = name )

class PseudoIndex( Pseudo ):
    def __init__( self, values, name ):
        super().__init__( data = values, name = name )

class PseudoColumns( Pseudo ):
    def __init__( self, values, name ):
        super().__init__( data = values, name = name )

# because the expression matrices can be really large and therefore take a long time to load
# this class will allow an easier shortcut by just extracting the column names and indices from
# the datafiles and offering the few methods that the Formatter class below will require to perform
# the actual reformatting. Hence, the Formatter can use this class just like it would a real pandas 
# DataFrame with all the actual data.

class PseudoDataFrame:
    """
    A class to imitate the relevant methods and attributes for re-formatting of a pandas DataFrame
    withou actually storing any of it's data.

    Parameters
    ----------
    source : str
        The data source file to read.
    sep : str
        The separator. By default tab.
    """
    def __init__( self, source : str, sep = "\t", **kwargs ):
        self.src = source
        self._sep = sep
        self.columns = None
        self.rows = None
        if self.src:
            self.read( self.src, sep = sep, **kwargs )
    
    def read( self, filename : str, index_col = 0, index_has_header = False, sep = "\t", **kwargs ) -> None:
        """
        Read a data source file and get the column (first line)
        names and the index column.

        Note
        ----
        The column names *must* be in the first line, no 
        comments may be present in the file!

        Parameters
        ----------
        filename : str
            The path to the data source file.
        index_col : int
            The index column. By default the first column.
        index_has_header : bool
            Set to True if the index column has a header.
        sep : str
            The separator. By default tab.
        """

        # get the first line which are the column names
        columns = subprocess.run( f"head -n 1 {filename}", shell=True, capture_output=True )
        columns = columns.stdout.decode( "utf-8" ).strip().split( sep )
        
        # get the first column with the index values
        index = str( index_col+1 )
        index = subprocess.run( f"cut -f { index } {filename}", shell=True, capture_output=True )
        index = index.stdout.decode( "utf-8" ).strip().split( "\n" )

        # get rid of a trailing whitespace
        if index[-1] == "":
            index = index[:-1]

        name = None
        if index_has_header:
            name = index[0]
            index = index[1:]

        self.columns = PseudoColumns( columns, None ) 
        self.index = PseudoIndex( index, name ) 
        self._replace_delims()


    def to_csv( self, filename : str = None, sep = "\t", **kwargs ):
        """
        Write the edited column names and indices to a csv file.

        Parameters
        ----------
        filename : str
            The path to the output file.
        sep : str
            The separator. By default tab.
        """
        if filename is None:
            filename = self.src

        tmpfile = f"{filename}.tmpfile"
        self._write_columns(tmpfile, sep)
        self._write_index(tmpfile)


    def _write_index(self, filename):
        """
        Write the index column to a file.
        """

        # first assemble the full column
        index_col = "\\n".join( self.index )
        if self.index.name is not None:
            index_col = f"{self.index.name}\\n{index_col}"
        
        # save the index col to another tmpfile
        index_file = f"{filename}.index_column"
        subprocess.run( f"printf '{index_col}' > { index_file }", shell=True )

        # and now paste the file and new index together and remove the tmpfiles...
        # cmd = f"""( paste <( printf '{index_col}' ) <( cut -f 2- '{filename}' ) )"""
        cmd = f"""( paste <( cut -f 1 '{index_file}' ) <( cut -f 2- '{filename}' ) ) ; rm {index_file} ; rm {filename}"""
        logger.debug( cmd )

        # subprocess.run( cmd, shell = True, executable = self._get_bash() )

        outfile = filename.replace( ".tmpfile", "" )
        with open( outfile, "w" ) as f:
            subprocess.run( cmd, shell = True, executable = self._get_bash(), stdout = f )

        # final = subprocess.run( cmd, shell = True, executable = self._get_bash(), capture_output = True )
        # final = final.stdout.decode( "utf-8" )
        # subprocess.run( f"echo '{final}' > {filename}", shell = True, executable = self._get_bash() )

    def _write_columns(self, filename, sep):
        """
        Write the column names to the first line.
        """
        # now assemble the first line
        first_line = sep.join( self.columns )

        # ----------------------------------------------------------------
        # this one works in theory but apparently the lines are too long and bash is not happy...
        # ----------------------------------------------------------------
        # # if no filename is given, just do the editing in-place...
        # if filename is None:
        #     options = ( "-i ", "" )
        # else:
        #     options = ( "", " > '{filename}'" )
        # # and insert the first line
        # subprocess.run( f"""sed { options[0] }"1s/.*/{first_line}/" '{self.src}'{ options[1].format(filename = filename) }""", shell = True, executable = self._get_bash() )

        
        with open( filename, "w" ) as f:
            f.write( first_line )
            f.write( "\n" )
        with open( filename, "a" ) as f:
            subprocess.run( f"""( tail -n +2 "{self.src}" ) """, shell = True, executable = self._get_bash(), stdout = f )

    def _get_bash(self):
        """
        Get the path to the used bash executable.
        """
        bash = subprocess.run( "which bash", shell = True, capture_output = True ).stdout.decode( "utf-8" ).strip()
        return bash

    def _replace_delims(self):
        """
        Removes any whitespace characters used for delimintation
        from the index and columns.
        """
        to_remove = ( "\n", "\t" )
        for i in to_remove:
            self.index = self.index.str.replace( i, "" )
            self.columns = self.columns.str.replace( i, "" )

    def __repr__(self):
        return f"PseudoDataFrame({self.columns}, {self.index})"

class Formatter:
    """
    A cass to read expression matrices and annotation files in `TSV` format, and re-format 
    the `ID`, `CellType`, and `Sample` columns (in annotation files), and `index` and `column names` 
    (expression matrices) to conform with EcoTyper format requirements.

    Parameters
    ----------
    formats : dict
        A dictionary of invalid characters which must be replaced with a valid character.     
    """
    def __init__( self, formats : dict = None ):
        
        self._formats = default_formats if not formats else formats
        
        self._matrices = {}
        self._annotations = {}

        self._matrix_filetypes = [ "*.counts", "*.countsTable", "*.tpm", "*.TPM" ]
        self._annotation_filetypes = [ "*.annotations", "*.annotation" ]

    def reformat( self ):
        """
        Reformat the expression matrix and annotation table.
        """
        logger.info( "Reformatting expression matrix and annotation table" )
        self._matrices = { k : self.reformat_expression_matrix( i ) for k,i in self._matrices.items() }
        self._annotations = { k : self.reformat_annotation_table( i ) for k,i in self._annotations.items() }
    
    def reformat_expression_matrix( self, matrix : pd.DataFrame ) -> pd.DataFrame:
        """
        Reformat the expression matrix' `index` and `column names`.
        """
        for old, new in self._formats.items():
            matrix.index = matrix.index.str.replace( old, new )
            matrix.columns = matrix.columns.str.replace( old, new )
        return matrix

    def reformat_annotation_table( self, table : pd.DataFrame ) -> pd.DataFrame:
        """
        Reformat the annotation table's `ID` column, the `CellType` column, and the `Sample` column.

        Note
        ----
        All of these columns must be present in the annotation table!

        """

        # first make sure they are all in string format
        table[ "ID" ] = table[ "ID" ].astype( str )
        table[ "CellType" ] = table[ "CellType" ].astype( str )
        table[ "Sample" ] = table[ "Sample" ].astype( str )

        for old, new in self._formats.items():
            table[ "ID" ] = table[ "ID" ].str.replace( old, new )
            table[ "CellType" ] = table[ "CellType" ].str.replace( old, new )
            table[ "Sample" ] = table[ "Sample" ].str.replace( old, new )
        return table

    def memory_saving_dir_pipe( self, path : str, output : str = None, suffix : str = None, **kwargs ) -> None:
        """
        This method performs the entire pipeline on all matching files within a directory
        but goes file-wise instead of step-by-step first reading all files, then formatting all files etc.
        This is computationally more expensive but uses less memory.

        Parameters
        ----------
        path : str
            The path to the directory containing the expression matrix and/or annotation table.
        
        output : str
            The path to the directory where the reformatted files will be written.

        suffix : str
            The suffix to append to the output file names.
        """
        matrices, annotations = self._read_from_dir( path )

        # now process each file:
        with alive_bar( len(annotations + matrices), title = "Processing files" ) as bar:
            
            kwargs1 = dict( kwargs )
            kwargs1.pop( "pseudo" )
            for i in annotations:
                logger.debug( "Reading annotation table", i )
                self.read_annotation_table( i, **kwargs1 )
                logger.debug( "Table has columns: ", self._annotations[ i ].columns )

                self.reformat()
                self.save_to_dir( path = output, suffix = suffix )
                self._annotations = {}
                bar()   

            kwargs.pop( "id_is_index" )
            for i in matrices:
                self.read_expression_matrix( i, **kwargs )
                self.reformat()
                self.save_to_dir( path = output, suffix = suffix )
                self._matrices = {}
                bar()



    def read_from_dir( self, path : str, **kwargs ):
        """
        Read an expression matrix and/or annotation table from the same directory.
        When using this method, it is assumed that expression matrix either ends with `.counts`, `.countsTable`, or `.tpm` and the annotation file ends with `.annotations`.


        Parameters
        ----------
        path : str
            The path to the directory containing the expression matrix and/or annotation table.
        """
        
        matrices, annotations = self._read_from_dir( path )

        # read the datafiles
        kwargs1 = dict(kwargs)
        kwargs1.pop( "pseudo" )
        self._annotations = { i : self._read_annotation_table( i, **kwargs1 ) for i in annotations }

        kwargs.pop( "id_is_index" )
        self._matrices = { i : self._read_expression_matrix( i, **kwargs ) for i in matrices }


    def _pseudoread_expression_matrix( self, filename : str, **kwargs ) -> PseudoDataFrame:
        """
        Only reads the first line and first column of the expression matrix.

        Parameters
        ----------
        filename : str
            The name of the expression matrix file.

        Returns
        -------
        PseudoDataFrame
            A pseudo dataframe containing the first line and first column of the expression matrix without actually reading any of the data.
            This object can still be "normally worked with" in terms of reformatting and saving.
        """
        return PseudoDataFrame( filename, **kwargs )

    def read_expression_matrix( self, file : str, pseudo : bool = False, **kwargs ):
        """
        Read an expression matrix.

        Parameters
        ----------
        file : str
            The path to the expression matrix.
        pseudo : bool
            If True, only the column names and index will be read into PseudoDataFrame.
            This will prevent excessive memory usage for large files.
        """
        logger.info( f"(this may take a while) Reading expression matrix {file}" )
        if pseudo:
            data = self._pseudoread_expression_matrix( file, **kwargs )
        else:
            data = self._read_expression_matrix( file, **kwargs )
        self._matrices[ file ] = data
        return data

    def read_annotation_table( self, file : str, id_is_index : bool = False, **kwargs ):
        """
        Read an annotation table.

        Parameters
        ----------
        file : str
            The path to the annotation table.
        id_is_index : bool
            Set to `True` if the `ID` column is the index of the table.
        """
        logger.info( f"(this may take a while) Reading annotation table {file}" )
        
        kwargs[ "id_is_index" ] = id_is_index
        data = self._read_annotation_table( file, **kwargs )
        self._annotations[ file ] = data
        return data

    def save_to_dir( self, path : str = None, suffix : str = None ):
        """
        Save the expression matrix and/or annotation table(s) to the same directory.
        When using this method, the same filenames as the input files will be re-used. 
        If saving to the same directory as the input files, this will overwrite the existing files!

        Parameters
        ----------
        path : str
            The path to the directory to save the expression matrix and/or annotation table.
            By default the same filenames as the input filenames will be used and the old files are overwritten.
        suffix : str
            Any suffix to add to the output filenames.
        """
        logger.info( f"(this may take a while) Saving to directory {path}" )

        make_path = self._create_make_path(path, suffix)

        for file,i in self._matrices.items():
            self.save_expression_matrix( make_path( file ), i )

        for file,i in self._annotations.items():    
            self.save_annotation_table(  make_path( file ), i )

    @staticmethod
    def _create_make_path(path : str, suffix : str = None ):
        """
        Create a lambda funtion that will create a proper 
        absolute filepath to store an output file to.

        Parameters
        ----------
        path : str
            The path to the directory to save the expression matrix and/or annotation table.
        suffix : str
            Any suffix to add to the output filenames.
        
        Returns
        -------
        make_path : lambda
            A lambda function that will create a proper absolute filepath to store an output file to.
        """
        if not suffix: suffix = ""
        if path: 
            if not os.path.exists( path ): 
                os.makedirs( path )
            if not os.path.isabs( path ):
                path = os.path.abspath( path )
            make_path = lambda x: f"{ path }/{ x }{ suffix }"
        else:
            make_path = lambda x: f"{ x }{ suffix }"
        return make_path


    @staticmethod
    def save_expression_matrix( file : str, matrix : pd.DataFrame ):
        """
        Save an expression matrix.

        Parameters
        ----------
        file : str
            The path to the expression matrix.
        matrix : pd.DataFrame
            The expression matrix to save.
        """
        logger.info( f"(this may take a while) Saving expression matrix {file}" )
        matrix.to_csv( file, sep = "\t", index = True )

    @staticmethod
    def save_annotation_table( file : str, table : pd.DataFrame ):
        """
        Save an annotation table.

        Parameters
        ----------
        file : str
            The path to the annotation table.
        table : pd.DataFrame
            The annotation table to save.
        """
        logger.info( f"(this may take a while) Saving annotation table {file}" )
        table.to_csv( file, sep = "\t", index = False )

    
    @staticmethod
    def _read_expression_matrix( file : str, **kwargs ):
        """
        Core of read_expression_matrix
        """
        data = pd.read_csv( file, sep = "\t", index_col = 0, **kwargs )
        return data

    @staticmethod
    def _read_annotation_table( file : str, id_is_index = False, **kwargs ):
        """
        Core of read_annotation_table
        """
        data = pd.read_csv( file, sep = "\t", **kwargs )
        if id_is_index:
            data.insert( 0, "ID", data.index )
            data = data.reset_index( drop = True )
        return data

    def _read_from_dir(self, path):
        """
        The core of read_from_dir
        """

        logger.info( f"Reading from directory {path}" )
        
        if not os.path.isabs( path ):
            path = os.path.abspath( path )

        # find matching datafiles
        pwd = os.getcwd()
        os.chdir( path )
        matrices = [ glob.glob( i ) for i in self._matrix_filetypes ]        
        annotations = [ glob.glob( i ) for i in self._annotation_filetypes ]
        os.chdir( pwd )

        # flatten the findings
        matrices = [ item for sublist in matrices for item in sublist ]
        annotations = [ item for sublist in annotations for item in sublist ]

        return matrices,annotations

    def _is_expression_matrix_file( self, path ):
        """
        Check if the file is an expression matrix file.
        """
        return any( path.endswith( i ) for i in self._matrix_filetypes )
    
    def _is_annotation_table_file( self, path ):
        """
        Check if the file is an annotation table file.
        """
        return any( path.endswith( i ) for i in self._annotation_filetypes )

    # these methods are used to get the read matrix 
    # in the main script in case only a single file is being read...
    def _last_matrix( self ):
        return list( self._matrices.values() )[-1]

    def _last_annotation( self ):
        return list( self._annotations.values() )[-1]
    
    @property
    def formats( self ):
        return self._formats

    @property
    def matrix_filetypes( self ):
        return self._matrix_filetypes
    
    @property
    def annotation_filetypes( self ):
        return self._annotation_filetypes
    
    @property
    def matrices( self ):
        return self._matrices
    
    @property
    def annotations( self ):
        return self._annotations
        
    
    def __repr__( self ):
        return f"Formatter( {self._formats} )"
    

